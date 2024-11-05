import json
from typing_extensions import override
from wrapperfunction.core import config
from openai import AzureOpenAI

from wrapperfunction.core.model.entity_setting import ChatbotSetting

client = AzureOpenAI(
    azure_endpoint=config.OPENAI_ENDPOINT,
    api_key=config.OPENAI_API_KEY,
    api_version=config.OPENAI_API_VERSION,
)


def generate_embeddings(text):
    return (
        client.embeddings.create(input=[text], model=config.OPENAI_EMB_MODEL)
        .data[0]
        .embedding
    )


def chat_completion_mydata(
    chatbot_setting: ChatbotSetting, chat_history, system_message
):
    completion = client.chat.completions.create(
        model=config.OPENAI_CHAT_MODEL,
        messages=chat_history,
        max_tokens=800,
        temperature=chatbot_setting.custom_settings.temperature,
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
                        "endpoint": config.SEARCH_ENDPOINT,
                        "index_name": chatbot_setting.index_name,
                        "semantic_configuration": chatbot_setting.index_name
                        + "-semantic-configuration",
                        "query_type": "vector_semantic_hybrid",
                        # "query_type": "vector",
                        "fields_mapping": {
                            "content_fields_separator": "\n",
                            "content_fields": ["chunk"],
                            "filepath_field": "metadata_storage_path",
                            "title_field": "title",
                            "url_field": "ref_url",
                            "vector_fields": ["text_vector"],
                        },
                        "in_scope": True,
                        "role_information": system_message,
                        "filter": None,
                        "strictness": 3,
                        "top_n_documents": 5,
                        "authentication": {"type": "api_key", "key": config.SEARCH_KEY},
                        "embedding_dependency": {
                            "type": "deployment_name",
                            "deployment_name": config.OPENAI_EMB_MODEL,
                        },
                    },
                }
            ]
        },
    )
    compl_data = json.loads(completion.choices[0].json())
    compl_data["usage"] = json.loads(completion.usage.json())
    return compl_data


def chat_completion(system_message, user_message):
    message_text = [{"role": "system", "content": system_message}]
    message_text.append({"role": "user", "content": user_message})
    completion = client.chat.completions.create(
        model=config.OPENAI_CHAT_MODEL,
        messages=message_text,
        temperature=0.7,
        max_tokens=1500,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    compl_data = json.loads(completion.choices[0].json())
    compl_data["usage"] = json.loads(completion.usage.json())
    return compl_data


@override
def chat_completion(chatbot_setting: ChatbotSetting, chat_history):
    completion = client.chat.completions.create(
        model=config.OPENAI_CHAT_MODEL,
        messages=chat_history,
        temperature=chatbot_setting.custom_settings.temperature,
        max_tokens=1500,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    compl_data = json.loads(completion.choices[0].json())
    compl_data["usage"] = json.loads(completion.usage.json())
    return compl_data
