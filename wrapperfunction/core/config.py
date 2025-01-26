import asyncio
import json
import os
from dotenv import load_dotenv
from wrapperfunction.core.model.entity_setting import ChatbotSetting, CustomSettings

# Load environment variables from .env file
load_dotenv()

# Define constants or functions to access environment variables
SEARCH_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_SERVICE_QUERY_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL")
OPENAI_EMB_MODEL = os.getenv("OPENAI_EMB_MODEL")
SPEECH_SERVICE_REGION = os.getenv("SPEECH_SERVICE_REGION")
SPEECH_SERVICE_KEY = os.getenv("SPEECH_SERVICE_KEY")
AVATAR_API_URL = os.getenv("AVATAR_API_URL")
AVATAR_AUTH_KEY = os.getenv("AVATAR_AUTH_KEY")
AVATAR_CODE = os.getenv("AVATAR_CODE")
AVATAR_CODE_FULL_SIZE = os.getenv("AVATAR_CODE_FULL_SIZE")
AVATAR_VOICE_ID = os.getenv("AVATAR_VOICE_ID")
AVATAR_VOICE_PROVIDER = os.getenv("AVATAR_VOICE_PROVIDER")
STORAGE_CONNECTION = os.getenv("STORAGE_CONNECTION")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
SUBFOLDER_NAME = os.getenv("SUBFOLDER_NAME")
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")
ENTITY_NAME = os.getenv("ENTITY_NAME")
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
MESSAGE_TABLE_NAME=os.getenv("COSMOS_MESSAGE_TABLE")
CONVERSATION_TABLE_NAME=os.getenv("COSMOS_CONVERSATION_TABLE")
AZURE_TEXT_ANALYTICS_ENDPOINT=os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
AZURE_TEXT_ANALYTICS_KEY=os.getenv("AZURE_TEXT_ANALYTICS_KEY")
STORAGE_ACCOUNT_KEY=os.getenv("STORAGE_ACCOUNT_KEY")
AZURE_IMAGE_ANALYTICS_ENDPOINT=os.getenv("AZURE_IMAGE_ANALYTICS_ENDPOINT")
AZURE_IMAGE_ANALYTICS_KEY=os.getenv("AZURE_IMAGE_ANALYTICS_KEY")
OPENAI_API_MODEL_VERSION=os.getenv("OPENAI_API_MODEL_VERSION")
COSMOS_VACATION_TABLE=os.getenv("COSMOS_VACATION_TABLE")
FAQ_TABLE_NAME=os.getenv("COSMOS_FAQ_TABLE")
COSMOS_SETTINGS_TABLE=os.getenv("COSMOS_SETTINGS_TABLE")
DEFAULT_ENTITY_SETTINGS=os.getenv("DEFAULT_ENTITY_SETTINGS")
SPEECH_SERVICE_ENDPOINT=os.getenv("SPEECH_SERVICE_ENDPOINT")
LDAP_SERVER=os.getenv("LDAP_SERVER")
LDAP_DOMAIN=os.getenv("LDAP_DOMAIN")
COSMOS_AUTH_USER_TABLE=os.getenv("COSMOS_AUTH_USER_TABLE")
COSMOS_AUTH_PERMISSION_TABLE=os.getenv("COSMOS_AUTH_PERMISSION_TABLE")
COSMOS_AUTH_USER_PER_TABLE=os.getenv("COSMOS_AUTH_USER_PER_TABLE")
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
BASE_URL=os.getenv("BASE_URL")
AUTH_ENABLED=os.environ.get("AUTH_ENABLED", "false").lower() == "true"


def load_entity_settings():
    from wrapperfunction.core.service import settings_service
    settings = settings_service.get_settings_by_entity(ENTITY_NAME)
    if len(settings) > 0:
        return settings[0]
    else:
        file_path = os.path.join(os.path.dirname(__file__), f"settings/{DEFAULT_ENTITY_SETTINGS}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                entity = json.load(file)
                entity["entity_name"] = ENTITY_NAME
                chatbot = entity.get("chatbots", [])
                chatbot[0]["index_name"] = ENTITY_NAME
                asyncio.create_task(
                    settings_service.add_setting(entity=entity)
                )      
                return entity

ENTITY_SETTINGS = load_entity_settings()
AR_DICT = ENTITY_SETTINGS.get("dict_AR", {})


def load_chatbot_settings(bot_name: str):
    chatbots_settings = ENTITY_SETTINGS.get("chatbots", [])
    chatbots = chatbots_settings if isinstance(chatbots_settings,list) else json.loads(chatbots_settings)
    for chatbot_obj in chatbots:
        if chatbot_obj["name"] == bot_name:
            custom_settings_data = chatbot_obj.get("custom_settings", {})
            temperature = custom_settings_data.get("temperature", None)
            max_tokens = custom_settings_data.get("max_tokens", 800)
            max_history_length= custom_settings_data.get("max_history_length", 9)
            top_p = custom_settings_data.get("top_p", 0.95)
            tools = custom_settings_data.get("tools",None)
            enable_history = chatbot_obj.get("enable_history", True)
            display_in_chat = chatbot_obj.get("display_in_chat", True)
            custom_settings = CustomSettings(temperature=temperature,
                                            top_p=top_p,
                                            max_tokens=max_tokens,
                                            tools=tools,
                                            max_history_length=max_history_length,
                                            display_in_chat=display_in_chat
                                        )
            chatbot = ChatbotSetting(

                name = chatbot_obj["name"],
                index_name = chatbot_obj.get("index_name", None),
                system_message = chatbot_obj["system_message"],
                examples = chatbot_obj.get("examples", []),
                custom_settings = custom_settings,
                enable_history=enable_history

            )
            return chatbot

    return ChatbotSetting(
        name=ENTITY_NAME,
        index_name=ENTITY_NAME,
        system_message="",
        examples=[],
        custom_settings=None,
        enable_history=True
    )