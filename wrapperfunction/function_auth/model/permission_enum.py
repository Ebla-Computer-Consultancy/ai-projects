from enum import Enum

from wrapperfunction.core import config


class PermissionTypes(Enum):
    ADMIN_CRAWLER = f"{config.BASE_URL}/api/v1/admin/crawler/"
    ADMIN_UPLOAD_BLOB = f"{config.BASE_URL}/api/v1/admin/upload-blobs/"
    ADMIN_GET_BLOB = f"{config.BASE_URL}/api/v1/admin/get-blobs/"#{container_name}
    ADMIN_GET_ALL_CONTAINERS = f"{config.BASE_URL}/api/v1/admin/get-containers"
    ADMIN_GET_SUBFOLDER = f"{config.BASE_URL}/api/v1/admin/get-subfolders/"#{container_name}
    ADMIN_DELETE_SUBFOLDER = f"{config.BASE_URL}/api/v1/admin/delete-subfolder"
    ADMIN_DELETE_BLOB_BY_METADATA = f"{config.BASE_URL}/api/v1/admin/delete-blob-by-metadata"
    ADMIN_DELETE_BLOB_BY_TITLE = f"{config.BASE_URL}/api/v1/admin/delete-blob-by-list-of-titles"
    ADMIN_RESET_INDEX = f"{config.BASE_URL}/api/v1/admin/reset-index/"#{index_name}
    ADMIN_RUN_INDEXER = f"{config.BASE_URL}/api/v1/admin/run-indexer/"#{index_name}
    ADMIN_INDEX_INFO = f"{config.BASE_URL}/api/v1/admin/index-info/"#{index_name}
    ADMIN_INDEXES_NAMES = f"{config.BASE_URL}/api/v1/admin/indexes-name"
    ADMIN_ADD_PERMISSION_TO_USER = f"{config.BASE_URL}/api/v1/admin/add-permission-to-user"
    ADMIN_ADD_PERMISSION_TO_TABLE = f"{config.BASE_URL}/api/v1/admin/add-permission-to-table"
    ADMIN = [ADMIN_CRAWLER,ADMIN_UPLOAD_BLOB,ADMIN_GET_BLOB,ADMIN_GET_ALL_CONTAINERS,ADMIN_GET_SUBFOLDER,ADMIN_DELETE_SUBFOLDER,ADMIN_DELETE_BLOB_BY_METADATA,ADMIN_DELETE_BLOB_BY_TITLE,ADMIN_RESET_INDEX,ADMIN_RUN_INDEXER,ADMIN_INDEX_INFO,ADMIN_INDEXES_NAMES,ADMIN_ADD_PERMISSION_TO_USER,ADMIN_ADD_PERMISSION_TO_USER]
    ##########################################################################
    MEDIA_GENERATE_REPORT = f"{config.BASE_URL}/api/v1/media/generate-report/"
    MEDIA_CRAWL = f"{config.BASE_URL}/api/v1/media/crawl/"
    MEDIA_SENTIMENT = f"{config.BASE_URL}/api/v1/media/sentiment/"
    MEDIA_DETECT_LANGUAGE = f"{config.BASE_URL}/api/v1/media/detect-language/"
    MEDIA_KEY_PHRASES = f"{config.BASE_URL}/api/v1/media/key-phrases/"
    MEDIA_ENTITY_RECOGNITION = f"{config.BASE_URL}/api/v1/media/entity-recognition/"
    MEDIA_IMAGE_ANALYSIS = f"{config.BASE_URL}/api/v1/media/image-analysis/"
    MEDIA_IMAGE_EMBEDDING = f"{config.BASE_URL}/api/v1/media/image-embedding/"
    MEDIA = [MEDIA_GENERATE_REPORT,MEDIA_CRAWL,MEDIA_SENTIMENT,MEDIA_DETECT_LANGUAGE,MEDIA_KEY_PHRASES,MEDIA_ENTITY_RECOGNITION,MEDIA_IMAGE_ANALYSIS,MEDIA_IMAGE_EMBEDDING]
    ##########################################################################
    CHATBOT_CHAT = f"{config.BASE_URL}/api/v1/chatbot/chat/"#{bot_name}
    CHATBOT_UPLOAD_DOCUMENT = f"{config.BASE_URL}/api/v1/chatbot/upload_documents/"
    CHATBOT = [CHATBOT_CHAT,CHATBOT_UPLOAD_DOCUMENT]
    ##########################################################################
    INTERACTIVE_DEPARTMENT_TYPES = f"{config.BASE_URL}/api/v1/interactive/department-types"
    INTERACTIVE_VACATION_TYPES = f"{config.BASE_URL}/api/v1/interactive/vacation-types"
    INTERACTIVE_SUBMIT_FORM = f"{config.BASE_URL}/api/v1/interactive/action/submit-form"
    INTERACTIVE_APPROVE = f"{config.BASE_URL}/api/v1/interactive/action/approve"
    INTERACTIVE_REJECT = f"{config.BASE_URL}/api/v1/interactive/action/reject"
    INTERACTIVE_PENDING = f"{config.BASE_URL}/api/v1/interactive/action/pending"
    INTERACTIVE_FILTER_FORMS = f"{config.BASE_URL}/api/v1/interactive/action/filter-vacation-forms-by"
    INTERACTIVE_ALL_FORMS = f"{config.BASE_URL}/api/v1/interactive/action/get-all-vacation-forms"
    INTERACTIVE_CHAT = [INTERACTIVE_DEPARTMENT_TYPES,INTERACTIVE_VACATION_TYPES,INTERACTIVE_SUBMIT_FORM,INTERACTIVE_APPROVE,INTERACTIVE_REJECT,INTERACTIVE_PENDING,INTERACTIVE_FILTER_FORMS,INTERACTIVE_ALL_FORMS]
    ##########################################################################
    AVATAR_START_STREAM = f"{config.BASE_URL}/api/v1/avatar/start-stream"
    AVATAR_SEND_CANDIDATE = f"{config.BASE_URL}/api/v1/avatar/send-candidate"
    AVATAR_SEND_ANSWER = f"{config.BASE_URL}/api/v1/avatar/send-answer"
    AVATAR_RENDER_TEXT = f"{config.BASE_URL}/api/v1/avatar/render-text"
    AVATAR_STOP_RENDER = f"{config.BASE_URL}/api/v1/avatar/stop-render"
    AVATAR_CLOSE_STREAM = f"{config.BASE_URL}/api/v1/avatar/close-stream"##{stream_id}
    AVATAR = [AVATAR_START_STREAM,AVATAR_SEND_CANDIDATE,AVATAR_SEND_ANSWER,AVATAR_RENDER_TEXT,AVATAR_STOP_RENDER,AVATAR_CLOSE_STREAM]
    ##########################################################################
    SPEECH_TOKEN=f"{config.BASE_URL}/api/v1/speech/token"     
    SPEECH_TRANSCRIPT=f"{config.BASE_URL}/api/v1/speech/transcript"   
    SPEECH = [SPEECH_TOKEN, SPEECH_TRANSCRIPT]
    ##########################################################################
    CHAT_HISTORY_CONVERSATION = f"{config.BASE_URL}/api/v1/chat-history/conversations/"
    CHAT_HISTORY_ALL_CONVERSATION = f"{config.BASE_URL}/api/v1/chat-history/all-conversations/"
    CHAT_HISTORY_CHAT = f"{config.BASE_URL}/api/v1/chat-history/chat/"
    CHAT_HISTORY_SENTIMENT = f"{config.BASE_URL}/api/v1/chat-history/add-feedback/"
    CHAT_HISTORY_ADD_FEEDBACK = f"{config.BASE_URL}/api/v1/chat-history/add-feedback/"
    CHAT_HISTORY_BOT_NAMES = f"{config.BASE_URL}/api/v1/chat-history/bot-names/"
    CHAT_HISTORY_ADD_MSG = f"{config.BASE_URL}/api/v1/chat-history/add-message/"
    CHAT_HISTORY = [CHAT_HISTORY_CONVERSATION,CHAT_HISTORY_ALL_CONVERSATION,CHAT_HISTORY_CHAT,CHAT_HISTORY_SENTIMENT,CHAT_HISTORY_ADD_FEEDBACK,CHAT_HISTORY_BOT_NAMES,CHAT_HISTORY_ADD_MSG]
    ##########################################################################
    DOCUMENT_INTELLIGENCE_ANALYZE_PDF = F"{config.BASE_URL}/api/v1/document-intelligence/analyze-pdf"
    DOCUMENT_INTELLIGENCE = [DOCUMENT_INTELLIGENCE_ANALYZE_PDF]
    ##########################################################################
    SEARCH_BOT_NAME = F"{config.BASE_URL}/api/v1/search/search/" ## {bot_name}
    SEARCH = [SEARCH_BOT_NAME]
    # SPEECH_token = ({"SPEECH":f"{config.BASE_URL}/api/v1/speech/token"})
    # SPEECH_transcript = ({"SPEECH":f"{config.BASE_URL}/api/v1/speech/transcript"})