import asyncio
import json
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from wrapperfunction.core.model.entity_setting import ChatbotSetting, CustomSettings
from wrapperfunction.media_monitoring.model.media_model import MediaInfo

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

VIDEO_INDEXER_KEY=os.getenv("VIDEO_INDEXER_KEY")
VIDEO_INDEXER_ACCOUNT_ID=os.getenv("VIDEO_INDEXER_ACCOUNT_ID")

COSMOS_VACATION_TABLE=os.getenv("COSMOS_VACATION_TABLE")
NAME=os.getenv("COSMOS_FAQ_TABLE")

COSMOS_FAQ_TABLE=os.getenv("COSMOS_FAQ_TABLE")

COSMOS_SETTINGS_TABLE=os.getenv("COSMOS_SETTINGS_TABLE")
DEFAULT_ENTITY_SETTINGS=os.getenv("DEFAULT_ENTITY_SETTINGS")
LDAP_SERVER=os.getenv("LDAP_SERVER")
LDAP_DOMAIN=os.getenv("LDAP_DOMAIN")
COSMOS_AUTH_USER_TABLE=os.getenv("COSMOS_AUTH_USER_TABLE")
COSMOS_AUTH_PERMISSION_TABLE=os.getenv("COSMOS_AUTH_PERMISSION_TABLE")
COSMOS_AUTH_USER_PER_TABLE=os.getenv("COSMOS_AUTH_USER_PER_TABLE")
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
BASE_URL=os.getenv("BASE_URL")
AUTH_ENABLED=os.environ.get("AUTH_ENABLED", "false").lower() == "true"
LDAP_ENABLED=os.environ.get("LDAP_ENABLED", "false").lower() == "true"
TENANT_ID=os.getenv("TENANT_ID")
CLIENT_ID=os.getenv("CLIENT_ID")
SUBSCRIPTION_ID=os.getenv("SUBSCRIPTION_ID")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
CLIENT_SECRET_VALUE=os.getenv("CLIENT_SECRET_VALUE")
RESOURCE_GROUP_NAME = os.getenv("RESOURCE_GROUP_NAME")
ACCOUNT_REGION=os.getenv("ACCOUNT_REGION")
SPEECH_RESOURCE_ID=os.getenv("SPEECH_RESOURCE_ID")
API_VERSION = os.getenv("API_VERSION")
SPEECH_SERVICE_ENDPOINT=os.getenv("SPEECH_SERVICE_ENDPOINT")
SEARCH_API_VERSION=os.getenv("SEARCH_API_VERSION")
COSMOS_MEDIA_KNOWLEDGE_TABLE=os.getenv("COSMOS_MEDIA_KNOWLEDGE_TABLE")
X_KEY=os.getenv("X_KEY")
X_TABLE=os.getenv("X_TABLE")
MOST_INDEXED_URLS_TABLE=os.getenv("MOST_INDEXED_URLS_TABLE")
MOST_USED_KEYWORDS_TABLE=os.getenv("MOST_USED_KEYWORDS_TABLE")


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
    chatbots = chatbots_settings if isinstance(chatbots_settings, list) else json.loads(chatbots_settings)
    for chatbot_obj in chatbots:
        if chatbot_obj["name"] == bot_name:
            custom_settings_data = chatbot_obj.get("custom_settings", {})
            temperature = custom_settings_data.get("temperature", None)
            max_tokens = custom_settings_data.get("max_tokens", 800)
            max_history_length = custom_settings_data.get("max_history_length", 9)
            top_p = custom_settings_data.get("top_p", 0.95)
            tools = custom_settings_data.get("tools", None)
            enable_history = chatbot_obj.get("enable_history", True)
            preserve_first_message = chatbot_obj.get("preserve_first_message", False)
            display_in_chat = custom_settings_data.get("display_in_chat", True)
            apply_sentiment = chatbot_obj.get("apply_sentiment", True) 


            custom_settings = CustomSettings(
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                tools=tools,
                max_history_length=max_history_length,
                display_in_chat=display_in_chat,

            )

            chatbot = ChatbotSetting(
                name=chatbot_obj["name"],
                index_name=chatbot_obj.get("index_name", None),
                system_message=chatbot_obj["system_message"],
                examples=chatbot_obj.get("examples", []),
                custom_settings=custom_settings,
                enable_history=enable_history,
                apply_sentiment=apply_sentiment,
                preserve_first_message=preserve_first_message,
            )
            return chatbot

    return ChatbotSetting(
        name=ENTITY_NAME,
        index_name=ENTITY_NAME,
        system_message="",
        examples=[],
        custom_settings=None,
        enable_history=True,
        preserve_first_message=False,
        apply_sentiment=True
    )


def get_media_info() -> MediaInfo:
    try:
        media_settings = ENTITY_SETTINGS.get("media_settings",{})
        info = media_settings.get("info",{}) if len(media_settings) > 0 else None
        if info is not None and len(info) > 0: 
            return MediaInfo(index_name=info.get("index_name","media"),
                             reports_container_name=info.get("reports_container_name","media-reports"),
                             container_name=info.get("container_name","media"))
        else:
            raise HTTPException(status_code=500, detail="There is no media setting info provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail="There is no media setting info provided")

