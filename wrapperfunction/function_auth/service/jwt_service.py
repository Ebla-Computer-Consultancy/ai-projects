from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from typing import Tuple
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User
from wrapperfunction.function_auth.service import table_service


# Function to create JWT tokens
def generate_jwt_tokens(user: User) -> Tuple[str, str]:
    try:
        if user.never_expire:
            now = now = datetime.utcnow()
            access_token = generate_access_token(user, time=now + timedelta(weeks=210))
            refresh_token = generate_refresh_token(user, time=now + timedelta(weeks=521))
        else:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
        return access_token, refresh_token
    except Exception as e:
        raise Exception("Error While Generating Tokens")

def generate_access_token(user: User, time: datetime = None) -> str:
    now = datetime.utcnow()
    # Create Access Token (1-hour expiration)
    access_token = jwt.encode(
            payload = {
                "name": user.username,
                "permissions": user.dict_permissions(),
                "enc_password": user.enc_password, 
                "exp": now + timedelta(hours=1) if time is None else time,
                "token_type": "access"
            },
            key = config.JWT_SECRET_KEY,
            algorithm=config.ALGORITHM
        )
    return access_token

def generate_refresh_token(user: User, time: datetime = None) -> str:
    now = datetime.utcnow()
    # Create Refresh Token (24-hours expiration)
    refresh_token = jwt.encode(
            payload = {
                "name": user.username,
                "permissions": user.dict_permissions(),
                "enc_password": user.enc_password, 
                "exp": now + timedelta(hours=24) if time is None else time,
                "token_type": "refresh"
            },
            key = config.JWT_SECRET_KEY,
            algorithm = config.ALGORITHM
        )
    return refresh_token

def update_refresh_token(token: str = None, user: dict = None):
    if token is None:
        token = generate_refresh_token(user)
    table_service.update_refresh_token(user, token)
    
# Function to decode and verify JWT tokens
def decode_jwt(token: str) -> User:
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.BASE_URL}/api/v1/user/login")
def get_token_from_header(authorization: str = Depends(oauth2_scheme)):
    if authorization.startswith("Bearer "):
        return authorization[7:]
    if authorization is not None or authorization is not "unknown":
        return authorization
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")