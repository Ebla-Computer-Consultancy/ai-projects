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

SPEECH_APP_REGION = os.getenv("APP_REGION")
SPEECH_SERVICE_KEY = os.getenv("SPEECH_SERVICE_KEY")