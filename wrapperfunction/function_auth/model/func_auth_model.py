from typing import List
from pydantic import BaseModel
from wrapperfunction.function_auth.model.permissions_model import Permission


class LoginRequest(BaseModel):
    username: str
    password: str


class User:
    def __init__(self,id: str, username: str,
    permissions: List[Permission],
    never_expire: bool = False):
        self.id = id
        self.username= username
        self.permissions= permissions
        self.never_expire= never_expire
    
    def dict_permissions(self):
        return [permission.to_dict() if not isinstance(permission, dict) else permission for permission in self.permissions]    
    
    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "permissions":self.dict_permissions(),
            "never_expire":self.never_expire
        }        
        
    
    