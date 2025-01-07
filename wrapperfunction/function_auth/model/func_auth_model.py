from typing import List
from pydantic import BaseModel
from wrapperfunction.function_auth.model.permissions_model import Permission


class LoginRequest(BaseModel):
    username: str
    password: str


class User:
    def __init__(self, username: str,
    enc_password: str,
    permissions: List[Permission]):
        self.username= username
        self.enc_password= enc_password
        self.permissions= permissions
    
    def dict_permissions(self):
        return [{"name":permission.get_permission_en_name(),"key":permission.get_permission_key()} for permission in self.permissions]    
    
    def to_dict(self):
        return {
            "username":self.username,
            "enc_password": self.enc_password,
            "permissions":self.dict_permissions()
        }        
        
    
    