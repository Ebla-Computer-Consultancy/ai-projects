from typing import Tuple
from fastapi import HTTPException, status
from ldap3 import NTLM, Connection, Server
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User, Permission
from wrapperfunction.function_auth.model.permissions_model import PermissionTypes
from wrapperfunction.function_auth.service import table_service
from wrapperfunction.function_auth.service import jwt_service
from wrapperfunction.function_auth.service.password_service import hash_password

def get_jwt(username: str, password: str):
    try:
        user = get_user(username, password)
        conn = test_ldap_connection(username=username, password=password)
        tokens = jwt_service.generate_jwt_tokens(user=user[0])
        jwt_service.update_refresh_token(token=tokens[1], user=user[1])
        return {"permissions": user[0].permissions,"access_token":tokens[0],"refresh_token":tokens[1]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
def test_ldap_connection(username: str, password: str):
    try:
        server = Server(config.LDAP_SERVER,get_info="ALL")
        conn = Connection(
            server,
            user=f'{config.LDAP_DOMAIN}\\{username}',
            password=password,
            authentication=NTLM
        )
        
        if conn.bind():
            return conn
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

def get_user(username, password) -> Tuple[User, dict]:
    try:
        user = table_service.get_user(username)
        if len(user) > 0:
            user_permissions = get_user_permissions(user[0]["user-id"])
            user_permissions = [
                    Permission(
                        en_name=permission_data["en_name"],
                        ar_name=permission_data["ar_name"],
                        key=permission_data["key"]
                    )
                    for permission in user_permissions
                    if (permission_data := table_service.get_permission_by_key(permission["permission"])[0])
                ]  
            return User(username=username,enc_password=hash_password(password),permissions=user_permissions),user[0]
        else: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
def get_user_permissions(user_id):
    return table_service.get_user_permissions(user_id)

def set_permission(url: str) -> str:
    if "interactive" in str(url):
        return PermissionTypes.INTERACTIVE_CHAT.value
    elif "search" in str(url):
        return PermissionTypes.SEARCH.value
    elif "chatbot" in str(url):
        return PermissionTypes.CHATBOT.value
    elif "media" in str(url):
        return PermissionTypes.MEDIA.value
    elif "avatar" in str(url):
        return PermissionTypes.AVATAR.value
    elif "speech" in str(url):
        return PermissionTypes.SPEECH.value
    elif "document-intelligence" in str(url):
        return PermissionTypes.DOCUMENT_INTELLIGENCE.value
    elif "chat-history" in str(url):
        return PermissionTypes.CHAT_HISTORY.value
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Required Permissions not found")

