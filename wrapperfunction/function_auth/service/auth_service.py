from datetime import datetime, timedelta
from typing import Tuple
from fastapi import HTTPException, Request, status
from ldap3 import NTLM, Connection, Server
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User, Permission
from wrapperfunction.function_auth.service import auth_db_service
from wrapperfunction.function_auth.service import jwt_service

### AUTHENTICATION
def authenticate_user(username: str, password: str):
    try:
        user = get_user(username)
        if test_ldap_connection(username=username, password=password)[0]:
            tokens = jwt_service.generate_jwt_tokens(user=user[0])
            jwt_service.update_refresh_token(token=tokens[1], user=user[1])
            return {
                "permissions": user[0].permissions,
                "access_token":tokens[0],
                "refresh_token":tokens[1]}
        else:
            raise Exception("LDAP: Connection Filed. User Not Found in AD")
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
        if config.AUTH_ENABLED:
            if conn.bind():
                return True, conn
            else:
                return False, conn
        else:
            return True, conn
    except Exception as e:
        raise Exception(f'LDAP: {str(e)}')

def get_user(username) -> Tuple[User, dict]:
    try:
        user = auth_db_service.get_user_by_username(username)
        if len(user) > 0:
            user_permissions = get_user_permissions(user[0]["_id"])
            all_permissions = auth_db_service.get_permissions()
            user_per_id = [per["permission_id"] for per in user_permissions]
            user_permissions = [
                    Permission(
                        id=permission["_id"],
                        en_name=permission["en_name"],
                        ar_name=permission["ar_name"],
                        key=permission["key"],
                        url=permission["url"]
                    )
                    for permission in all_permissions
                    if (permission["_id"] in user_per_id)
                ]  
            return User(id=user[0]["_id"],username=username,permissions=user_permissions,never_expire=user[0]["never_expire"]),user[0]
        else: 
            raise Exception("User Not Found")
    except Exception as e:
        raise Exception(f"{str(e)}")
        
def get_user_permissions(user_id):
    return auth_db_service.get_user_permissions(user_id)

def update_refresh_token(token: str):
    try:
        payloads = jwt_service.decode_jwt(token)
        user = User(id=payloads["id"],username=payloads["name"],permissions=payloads["permissions"])
        if payloads["token_type"] == "refresh":
            entity_user = auth_db_service.get_user_by_refresh_token(token=token, user_id=user.id)
            if len(entity_user) < 1:
                raise Exception(f"Invalid refresh_token")
            now = datetime.utcnow()
            refresh_time = timedelta(minutes=int(config.ENTITY_SETTINGS["refresh_token_valid_time"]))
            new_refresh_token = jwt_service.generate_refresh_token(user=user, time=now + refresh_time)
            jwt_service.update_refresh_token(token=new_refresh_token,user=entity_user[0])
            return {"refresh_token":new_refresh_token}
        else:
            raise Exception(f"Can't update using access_token")
    except Exception as e:
        raise Exception(f"{str(e)}")

def get_access_token(token: str):
    try:
        payloads = jwt_service.decode_jwt(token)
        user = User(id=payloads["id"],username=payloads["name"],permissions=payloads["permissions"])
        if payloads["token_type"] == "refresh":
            entity_user = auth_db_service.get_user_by_refresh_token(token=token, user_id=user.id)
            if len(entity_user) < 1:
                raise Exception(f"Invalid refresh_token")
        now = datetime.utcnow()
        access_time = timedelta(minutes=int(config.ENTITY_SETTINGS["access_token_valid_time"]))
        new_access_token = jwt_service.generate_access_token(user=user, time=now + access_time)
        return {"access_token":new_access_token}
    except Exception as e:
        raise Exception(f"{str(e)}")

### AUTHORIZATION
def hasAnyAuthority(request: Request, token: str, permission: str):
    try:
        payloads = jwt_service.decode_jwt(token)
        user = User(id=payloads["id"],username=payloads["name"],permissions=payloads["permissions"])
        if payloads["token_type"] == "refresh":
            if len(auth_db_service.get_user_by_refresh_token(token=token, user_id=user.username)) < 1:
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
            
        
        