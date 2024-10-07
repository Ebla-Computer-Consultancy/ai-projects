import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define constants or functions to access environment variables
SEARCH_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_SERVICE_QUERY_KEY")
SEARCH_INDEX = os.getenv("SEARCH_INDEX_NAME")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL")
OPENAI_EMB_MODEL = os.getenv("OPENAI_EMB_MODEL")

RERA_STORAGE_CONNECTION = os.getenv("RERA_STORAGE_CONNECTION")
RERA_VOICES_CONTAINER = os.getenv("RERA_VOICES_CONTAINER")

SPEECH_SERVICE_REGION = os.getenv("SPEECH_SERVICE_REGION")
SPEECH_SERVICE_KEY = os.getenv("SPEECH_SERVICE_KEY")

AVATAR_API_URL = os.getenv('AVATAR_API_URL')
AVATAR_AUTH_KEY = os.getenv('AVATAR_AUTH_KEY') 
AVATAR_CODE= os.getenv('AVATAR_CODE')
AVATAR_CODE_FULL_SIZE = os.getenv('AVATAR_CODE_FULL_SIZE')
AVATAR_VOICE_ID= os.getenv('AVATAR_VOICE_ID')
AVATAR_VOICE_PROVIDER= os.getenv('AVATAR_VOICE_PROVIDER')

RERA_STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME')
RERA_CONTAINER_NAME = os.getenv('CONTAINER_NAME')
RERA_SUBFOLDER_NAME = os.getenv('SUBFOLDER_NAME')
RERA_DOCS_SUBFOLDER_NAME = os.getenv('DOCS_SUBFOLDER_NAME')

SYSTEM_MESSAGE=os.getenv('SYSTEM_MESSAGE')

def load_ar_replacement_data():
    file_path = os.path.join(os.path.dirname(__file__), f'dict_AR/{SEARCH_INDEX}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {}
    

AR_DICT = load_ar_replacement_data()