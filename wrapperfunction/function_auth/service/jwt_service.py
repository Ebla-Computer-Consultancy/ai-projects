from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from typing import Tuple
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User
from wrapperfunction.function_auth.service import auth_db_service


# Function to create JWT tokens
def generate_jwt_tokens(user: User) -> Tuple[str, str]:
    try:
        now = datetime.utcnow()
        access_time = timedelta(minutes=int(config.ENTITY_SETTINGS["access_token_valid_time"]))
        refresh_time = timedelta(minutes=int(config.ENTITY_SETTINGS["refresh_token_valid_time"]))
        
        if user.never_expire:
            access_time = timedelta(weeks=210)
            refresh_time = timedelta(weeks=521)

        access_token = generate_access_token(user, now + access_time)
        refresh_token = generate_refresh_token(user, now + refresh_time)
        
        return access_token, refresh_token
    except Exception as e:
        raise Exception(f"Error While Generating Tokens: {str(e)}")

def generate_access_token(user: User, time: datetime) -> str:
    access_token = jwt.encode(
            payload = {
                "id": user.id,
                "name": user.username,
                "permissions": user.dict_permissions(),
                "exp": time,
                "token_type": "access"
            },
            key = config.JWT_SECRET_KEY,
            algorithm=config.ALGORITHM
        )
    return access_token

def generate_refresh_token(user: User, time: datetime) -> str:
    refresh_token = jwt.encode(
            payload = {
                "id": user.id,
                "name": user.username,
                "permissions": user.dict_permissions(), 
                "exp": time,
                "token_type": "refresh"
            },
            key = config.JWT_SECRET_KEY,
            algorithm = config.ALGORITHM
        )
    return refresh_token

def update_refresh_token(token: str = None, user: dict = None):
    if token is None:
        token = generate_refresh_token(user)
    auth_db_service.update_refresh_token(user, token)
    
# Function to decode and verify JWT tokens
def decode_jwt(token: str) -> User:
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.BASE_URL}/api/v1/user/swagger/login")
def get_token_from_header(authorization: str = Depends(oauth2_scheme)):
    if authorization.startswith("Bearer "):
        return authorization[7:]
    if authorization != None or authorization != "unknown":
        return authorization
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")