import os
import json
from typing import List
from enum import Enum
import uuid

# Open Ai
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv

# Fast Api
from fastapi import FastAPI, UploadFile, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import search namespaces
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

import wrapperFunction.services.speech as speech
from wrapperFunction.utils.blobStorage import (
    delete_blob_snapshots,
    download_blob_from_container,
    upload_to_blob_container,
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://github.com/Ebla-Computer-Consultancy",
        "http://localhost",
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Roles = Enum(
    "Roles",
    {
        "User": "user",
        "Assistant": "assistant",
        "Error": "error",
        "Tool": "tool",
        "Function": "function",
        "System": "system",
    },
)


class ChatMessage(BaseModel):
    content: str
    role: Roles

    class Config:
        use_enum_values = True


class searchCriteria(BaseModel):
    query: str
    facet: str = None
    sort: str = None


# Azure Search constants
load_dotenv()
search_endpoint = os.getenv("SEARCH_SERVICE_ENDPOINT")
search_key = os.getenv("SEARCH_SERVICE_QUERY_KEY")
search_index = os.getenv("SEARCH_INDEX_NAME")
openai_api_type = os.getenv("OPENAI_API_TYPE")
openai_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_api_version = os.getenv("OPENAI_API_VERSION")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_chat_model = os.getenv("OPENAI_CHAT_MODEL")
openai_emb_model = os.getenv("OPENAI_EMB_MODEL")
rera_storage_connection = os.getenv("RERA_STORAGE_CONNECTION")
rera_voices_container = os.getenv("RERA_VOICES_CONTAINER")
# Wrapper function for request to search index


openai.api_type = openai_api_type

client = AzureOpenAI(
    azure_endpoint=openai_endpoint,
    api_key=openai_api_key,
    api_version=openai_api_version,
)


def search_query(search_text, filter_by=None, sort_order=None):
    try:
        # Create a search client
        azure_credential = AzureKeyCredential(search_key)
        search_client = SearchClient(search_endpoint, search_index, azure_credential)

        jsonResult = []
        results = search_client.search(
            search_text=search_text,
            vector_queries=[
                {
                    "kind": "vector",
                    "vector": utils.generate_embeddings(
                        client, search_text, openai_emb_model
                    ),
                    "fields": "text_vector",
                    "k": 10,
                }
            ],
            include_total_count=True,
        )
        for result in results:
            jsonResult.append(json.loads(json.dumps(dict(result))))
        return jsonResult

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


@app.post("/demo/v0.1/search-action")
def search(rs: searchCriteria):
    try:
        # Get the search terms from the request form
        search_text = rs.query
        # If a facet is selected, use it in a filter
        filter_expression = None
        if rs.facet:
            filter_expression = "metadata_author eq '{0}'".format(rs.facet)

        # If a sort field is specified, modify the search expression accordingly
        sort_expression = "search.score()"
        sort_field = "relevance"  # default sort is search.score(), which is relevance
        if rs.sort:
            sort_field = rs.sort
            if sort_field == "file_name":
                sort_expression = "metadata_storage_name asc"
            elif sort_field == "size":
                sort_expression = "metadata_storage_size desc"
            elif sort_field == "date":
                sort_expression = "metadata_storage_last_modified desc"
            elif sort_field == "sentiment":
                sort_expression = "sentiment desc"

        # submit the query and get the results
        results = search_query(search_text, filter_expression, sort_expression)
        # render the results
        return {"count": len(results), "rs": results}

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


@app.post("/demo/v0.1/chat-action")
def chat(messageHistory: List[ChatMessage]):
    try:
        chat_history_arr = messageHistory
        if bool(len([x for x in chat_history_arr if x.role == "system"])):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "system messages is not allowed"
            )
        chat_history = []
        for item in chat_history_arr:
            chat_history.append(item.model_dump())
        # Get response from OpenAI ChatGPT
        completion = client.chat.completions.create(
            model=openai_chat_model,
            messages=chat_history,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": search_endpoint,
                            "index_name": search_index,
                            # "semantic_configuration": search_index+"-semantic-configuration",
                            # "query_type": "vector_semantic_hybrid",
                            "query_type": "vector",
                            "fields_mapping": {
                                "content_fields_separator": "\n",
                                "content_fields": ["chunk"],
                                "filepath_field": "title",
                                "title_field": "chunk_id",
                                "url_field": "metadata_storage_path",
                                "vector_fields": ["text_vector"],
                            },
                            "in_scope": True,
                            "role_information": "You are an AI assistant that helps people find information using the defined datasource. always reply in the same question language. and give long and descriptive answers",
                            "filter": None,
                            "strictness": 3,
                            "top_n_documents": 5,
                            "authentication": {"type": "api_key", "key": search_key},
                            "embedding_dependency": {
                                "type": "deployment_name",
                                "deployment_name": openai_emb_model,
                            },
                        },
                    }
                ]
            },
        )
        return json.loads(completion.choices[0].json())
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


@app.post("/demo/v0.1/transcribe")
async def transcribe(file: UploadFile):
    splittedFileName = file.filename.lower().split(".")
    fileExtension = splittedFileName[len(splittedFileName) - 1]

    if fileExtension != "wav":
        raise HTTPException(
            400, f"file type { fileExtension } not allowed \n use wav audio files"
        )

    voice_name = f"voice_{uuid.uuid4()}.wav"
    download_file_path = f"voices/{voice_name}"
    await upload_to_blob_container(
        file, rera_storage_connection, rera_voices_container, voice_name
    )
    download_blob_from_container(
        rera_storage_connection, rera_voices_container, download_file_path, voice_name
    )
    transcription_result = speech.transcribe_audio_file(download_file_path)
    os.remove(download_file_path)
    delete_blob_snapshots(
        connection_string=rera_storage_connection,
        container_name=rera_voices_container,
        blob_name=voice_name,
    )
    return transcription_result
