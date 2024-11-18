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
RERA_VOICES_CONTAINER = os.getenv("RERA_VOICES_CONTAINER")
SPEECH_SERVICE_REGION = os.getenv("SPEECH_SERVICE_REGION")
SPEECH_SERVICE_KEY = os.getenv("SPEECH_SERVICE_KEY")
AVATAR_API_URL = os.getenv("AVATAR_API_URL")
AVATAR_AUTH_KEY = os.getenv("AVATAR_AUTH_KEY")
AVATAR_CODE = os.getenv("AVATAR_CODE")
AVATAR_CODE_FULL_SIZE = os.getenv("AVATAR_CODE_FULL_SIZE")
AVATAR_VOICE_ID = os.getenv("AVATAR_VOICE_ID")
AVATAR_VOICE_PROVIDER = os.getenv("AVATAR_VOICE_PROVIDER")
RERA_STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
RERA_STORAGE_CONNECTION = os.getenv("RERA_STORAGE_CONNECTION")
RERA_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
RERA_SUBFOLDER_NAME = os.getenv("SUBFOLDER_NAME")
RERA_DOCS_SUBFOLDER_NAME = os.getenv("DOCS_SUBFOLDER_NAME")
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")
SYSTEM_MESSAGE=os.getenv('SYSTEM_MESSAGE')
ENTITY_NAME = os.getenv("ENTITY_NAME")
CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
MESSAGE_TABLE_NAME=os.getenv("COSMOS_MESSAGE_TABLE")
CONVERSATION_TABLE_NAME=os.getenv("COSMOS_CVONVERSATION_TABLE")
AZURE_TEXT_ANALYTICS_ENDPOINT=os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
AZURE_TEXT_ANALYTICS_KEY=os.getenv("AZURE_TEXT_ANALYTICS_KEY")
def load_entity_settings():
    file_path = os.path.join(os.path.dirname(__file__), f"settings/{ENTITY_NAME}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {}


ENTITY_SETTINGS = load_entity_settings()
AR_DICT = ENTITY_SETTINGS.get("dict_AR", {})


def load_chatbot_settings(bot_name: str):
    for chatbot_obj in ENTITY_SETTINGS.get("chatbots", []):
        if chatbot_obj["name"] == bot_name:
            custom_settings_data = chatbot_obj.get("custom_settings", {})
            temperature = custom_settings_data.get("temperature", None)
            tools = custom_settings_data.get("tools",None)
            custom_settings = CustomSettings(temperature=temperature) # Duplicated line
            custom_settings = CustomSettings(temperature=temperature, tools=tools)
            chatbot = ChatbotSetting(
                name = chatbot_obj["name"],
                index_name = chatbot_obj.get("index_name", None),
                system_message = chatbot_obj["system_message"],
                examples = chatbot_obj.get("examples", []),
                custom_settings = custom_settings,
            )
            return chatbot

    return ChatbotSetting(
        name=ENTITY_NAME,
        index_name=ENTITY_NAME,
        system_message="",
        examples=[],
        custom_settings=None,
    )
