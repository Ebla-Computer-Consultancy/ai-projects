import json
from wrapperfunction.core import config
from openai import AzureOpenAI
from wrapperfunction.core.model.entity_setting import ChatbotSetting

client = AzureOpenAI(
    azure_endpoint=config.OPENAI_ENDPOINT,
    api_key=config.OPENAI_API_KEY,
    api_version=config.OPENAI_API_VERSION,
)


def chat_completion(chatbot_setting: ChatbotSetting, chat_history,category_result=None):
    extra_body = {}
    tools_description = None
    tool_choice = None
    if chatbot_setting.index_name:
        extra_body = set_extra_body(chatbot_setting,category_result)
    if chatbot_setting.custom_settings.tools:
        tools_description = chatbot_setting.custom_settings.tools
        tool_choice = "auto"
    completion = client.chat.completions.create(
        model=config.OPENAI_CHAT_MODEL,
        messages=chat_history,
        max_tokens=chatbot_setting.custom_settings.max_tokens,
        temperature=chatbot_setting.custom_settings.temperature,
        top_p=chatbot_setting.custom_settings.top_p,
        frequency_penalty=0,
        presence_penalty=0,
        tools=tools_description,
        tool_choice=tool_choice,
        stop=None,
        stream=False,
        extra_body=extra_body,
    )
    completion_data = json.loads(completion.choices[0].json())
    completion_data["usage"] = json.loads(completion.usage.json())
    if completion_data["message"]["tool_calls"]:
        completion_data["message"]["tool_calls"] = getToolCalls(completion_data["message"]["tool_calls"])
    return completion_data


def generate_embeddings(text):
    return (
        client.embeddings.create(input=[text], model=config.OPENAI_EMB_MODEL)
        .data[0]
        .embedding
    )

def getToolCalls(tool_calls):
    return [
        {
            **json.loads(json.dumps(tool_call)),  
            "function": {
                **tool_call["function"],
                "arguments": json.loads(tool_call["function"]["arguments"])
            }
        }
        for tool_call in tool_calls
    ]

def set_extra_body(chatbot_setting: ChatbotSetting, category_result=None):
    return {
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
                    "role_information": chatbot_setting.system_message,
                    "filter": chatbot_setting.custom_settings.filter_exp,
                    "strictness": 3,
                    "top_n_documents":5,
                    "authentication": {"type": "api_key", "key": config.SEARCH_KEY},
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": config.OPENAI_EMB_MODEL,
                    },
                },
            }
        ]
    }