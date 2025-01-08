from wrapperfunction.function_auth.model.permission_enum import PermissionTypes
from wrapperfunction.function_auth.service import table_service
class Permission:
    def __init__(self, key: str,
    en_name: str, ar_name, type: str):
        
        self.__key = key
        self.__en_name = en_name
        self.__ar_name = ar_name
        self.__type = type
        
    def get_permission_key(self):
        return self.__key
    
    def get_permission_en_name(self):
        return self.__en_name

    def get_permission_ar_name(self):
        return self.__ar_name
    
    def get_permission_type(self):
        return self.__type

class ChatbotPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.CHATBOT.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])
    
class InteractivePermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.INTERACTIVE_CHAT.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])

class MediaPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.MEDIA.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])
        
class SearchPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.SEARCH.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])
        
class SpeechPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.SPEECH.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])
        
class AvatarPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.AVATAR.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])
        
class DocumentIntelligencePermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.DOCUMENT_INTELLIGENCE.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])
        
class ChathistoryPermission(Permission):
    def __init__(self):
        res = table_service.get_permission_by_name(name=PermissionTypes.CHAT_HISTORY.value)[0]
        super().__init__(res["key"], res["en_name"], res["ar_name"], res["type"])