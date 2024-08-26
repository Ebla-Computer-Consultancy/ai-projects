import os
import json
from typing import List
from enum import Enum

# Open Ai
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv

# Fast Api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import search namespaces
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

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

        # Submit search query
        """ results =  search_client.search(search_text,
                                        search_mode="all",
                                        include_total_count=True,
                                        filter=filter_by,
                                        order_by=sort_order,
                                        facets=['metadata_author'],
                                        highlight_fields='merged_content-3,imageCaption-3',
                                        select = "url,metadata_storage_name,metadata_author,metadata_storage_size,metadata_storage_last_modified,language,sentiment,merged_content,keyphrases,locations,imageTags,imageCaption")
        """

        jsonResult = []
        results = search_client.search(
            search_text=search_text,
            vector_queries=[
                {
                    "kind": "vector",
                    "vector": generate_embeddings(search_text, openai_emb_model),
                    "fields": "text_vector",
                    #   "fields": "contentVector",
                    "k": 10,
                }
            ],
            # query_type="semantic",
            # semantic_configuration_name=search_index+"-semantic-configuration",
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
        chat_history = []
        for item in chat_history_arr:
            chat_history.append(item.dict())
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
                            "role_information": "You are a language detector that detects the input language and responds in the same language. You must add Arabic diacritics to your output answer if the prompt is in Arabic",
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


def generate_embeddings(text, model):  # model = "deployment_name"
    return client.embeddings.create(input=[text], model=model).data[0].embedding
