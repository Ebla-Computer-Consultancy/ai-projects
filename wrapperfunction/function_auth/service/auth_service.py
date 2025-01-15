from typing import Tuple
from fastapi import HTTPException, Request, status
from ldap3 import NTLM, Connection, Server
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User, Permission
from wrapperfunction.function_auth.service import table_service
from wrapperfunction.function_auth.service import jwt_service

### AUTHENTICATION
def get_jwt(username: str, password: str):
    try:
        user = get_user(username)
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

def get_user(username) -> Tuple[User, dict]:
    try:
        user = table_service.get_user_by_name(username)
        if len(user) > 0:
            user_permissions = get_user_permissions(user[0]["_id"])
            user_permissions = [
                    Permission(
                        id=permission_data["_id"],
                        en_name=permission_data["en_name"],
                        ar_name=permission_data["ar_name"],
                        key=permission_data["key"],
                        url=permission_data["url"]
                    )
                    for permission in user_permissions
                    if (permission_data := table_service.get_permission_by_id(permission["permission_id"])[0])
                ]  
            return User(id=user[0]["_id"],username=username,permissions=user_permissions,never_expire=user[0]["never_expire"]),user[0]
        else: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
def get_user_permissions(user_id):
    return table_service.get_user_permissions(user_id)

def update_refresh_token(token: str):
    try:
        payloads = jwt_service.decode_jwt(token)
        user = User(id=payloads["id"],username=payloads["name"],permissions=payloads["permissions"])
        if payloads["token_type"] == "refresh":
            entity_user = table_service.get_user_by_token(token=token, user_id=user.id)
            if len(entity_user) < 1:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid refresh_token")
            new_refresh_token = jwt_service.generate_refresh_token(user=user)
            jwt_service.update_refresh_token(token=new_refresh_token,user=entity_user[0])
            return {"refresh_token":new_refresh_token}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Cun't update using access_token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{str(e)}")

### AUTHORIZATION
def hasAnyAuthority(request: Request, token: str, permission: str):
    try:
        payloads = jwt_service.decode_jwt(token)
        user = User(id=payloads["id"],username=payloads["name"],permissions=payloads["permissions"])
        if payloads["token_type"] == "refresh":
            if len(table_service.get_user_by_token(token=token, user_id=user.username)) < 1:
                raise Exception(f"Invalid refresh_token")
        have_permission = False
        for user_per in user.permissions:
            # if user have the routes permission
            if permission == user_per["key"]:
                have_permission = True
                break
            # if user have the level one permission
            if user_per["url"] in str(request.url):
                have_permission = True
                break 
        if not have_permission:    
            raise Exception(f"User '{user.username}' don't have the required permission to access this endpoint")
    except Exception as e:
        raise Exception(f"{str(e)}") 
            
        
        