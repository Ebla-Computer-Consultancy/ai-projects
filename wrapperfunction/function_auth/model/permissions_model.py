
class Permission:
    def __init__(self, id: str,
    en_name: str, ar_name, key: str, url: str = None):
        
        self.__id = id
        self.__en_name = en_name
        self.__ar_name = ar_name
        self.__key = key
        self.__url = url
        
    def to_dict(self):
        return {
            "id":self.__id,
            "en_name":self.__en_name,
            "ar_name":self.__ar_name,
            "key":self.__key,
            "url": self.__url
        }
        
    def get_permission_key(self):
        return self.__key
    
    def get_permission_en_name(self):
        return self.__en_name

    def get_permission_ar_name(self):
        return self.__ar_name
    
    def get_permission_id(self):
        return self.__id
    
    def get_permission_url(self):
        return self.__url