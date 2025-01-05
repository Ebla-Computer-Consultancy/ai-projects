from fastapi import HTTPException
from ldap3 import NTLM, Connection, Server
from passlib.context import CryptContext
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User
from wrapperfunction.function_auth.service import table_service
from wrapperfunction.function_auth.service.jwt_service import generate_jwt_tokens

def get_jwt(username: str, password: str):
    try:
        user = get_user(username, password)
        conn = test_ldap_connection(username=username, password=password)
        tokens = generate_jwt_tokens(user=user)
        return {"permissions": user.permissions,"access_token":tokens[0],"refresh_token":tokens[1]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
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
            raise HTTPException(status_code=401,detail="Unauthorized: User Not Found")
    except Exception as e:
        raise HTTPException(status_code=401,detail="Unauthorized")

def get_user(username, password):
    try:
        user = table_service.get_user(username)
        if len(user) > 0:
            user_permissions = get_user_permissions(user[0]["user-id"])
            user_permissions = [permission["permission"] for permission in user_permissions]   
            return User(username=username,enc_password=hash_password(password),permissions=user_permissions)
        else: 
            raise HTTPException(status_code=404, detail="User Not Found")
    except Exception as e:
        raise HTTPException(status_code=404, detail="User Not Found")

def get_user_permissions(user_id):
    return table_service.get_user_permissions(user_id)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)