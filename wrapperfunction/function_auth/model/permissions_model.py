from enum import Enum
from wrapperfunction.function_auth.service import table_service

class PermissionTypes(Enum):
    CHATBOT = "CHATBOT"
    MEDIA = "MEDIA"
    INTERACTIVE_CHAT = "INTERACTIVE_CHAT"
    SEARCH = "SEARCH"
    AVATAR = "AVATAR"
    SPEECH = "SPEECH"
    DOCUMENT_INTELLIGENCE = "DOCUMENT_INTELLIGENCE"
    CHAT_HISTORY = "CHAT_HISTORY"

class Permission:
    def __init__(self, key: str,
    name: str):
        
        self.__key = key
        self.__name = name
        
    def get_permission_key(self):
        return self.__key
    
    def get_permission_name(self):
        return self.__name

class ChatbotPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.CHATBOT.value)[0]
        super().__init__(res["key"], res["name"])
    
class InteractivePermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.INTERACTIVE_CHAT.value)[0]
        super().__init__(res["key"], res["name"])

class MediaPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.MEDIA.value)[0]
        super().__init__(res["key"], res["name"])
        
class SearchPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.SEARCH.value)[0]
        super().__init__(res["key"], res["name"])
        
class SpeechPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.SPEECH.value)[0]
        super().__init__(res["key"], res["name"])
        
class AvatarPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.AVATAR.value)[0]
        super().__init__(res["key"], res["name"])
        
class DocumentIntelligencePermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.DOCUMENT_INTELLIGENCE.value)[0]
        super().__init__(res["key"], res["name"])
        
class ChathistoryPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.CHAT_HISTORY.value)[0]
        super().__init__(res["key"], res["name"])