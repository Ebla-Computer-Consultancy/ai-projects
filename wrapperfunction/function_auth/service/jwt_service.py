from fastapi import HTTPException, Header, status
import jwt
from datetime import datetime, timedelta
from typing import Tuple
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User
from wrapperfunction.function_auth.service import table_service


# Function to create JWT tokens
def generate_jwt_tokens(user: User) -> Tuple[str, str]:
    try:
        # Create Access Token (1-hour expiration)
        access_token = generate_access_token(user)

        # Create Refresh Token (24-hour expiration)
        refresh_token = generate_refresh_token(user)

        return access_token, refresh_token
    except Exception as e:
        raise Exception("Error While Generating Tokens")

def generate_access_token(user: User) -> str:
    now = datetime.utcnow()
    # Create Access Token (1-hour expiration)
    access_token = jwt.encode(
            payload = {
                "name": user.username,
                "permissions": user.dict_permissions(),
                "enc_password": user.enc_password, 
                "exp": now + timedelta(hours=1),
                "token_type": "access"
            },
            key = config.JWT_SECRET_KEY,
            algorithm=config.ALGORITHM
        )
    return access_token

def generate_refresh_token(user: User) -> str:
    now = datetime.utcnow()
    # Create Refresh Token (24-hours expiration)
    refresh_token = jwt.encode(
            payload = {
                "name": user.username,
                "permissions": user.dict_permissions(),
                "enc_password": user.enc_password, 
                "exp": now + timedelta(hours=24),
                "token_type": "refresh"
            },
            key = config.JWT_SECRET_KEY,
            algorithm = config.ALGORITHM
        )
    return refresh_token

def update_refresh_token(token: str = None, user: User = None):
    if token is None:
        token = generate_refresh_token(user)
    table_service.update_refresh_token(user, token)
    
# Function to decode and verify JWT tokens
def decode_jwt(token: str) -> User:
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Invalid token")

def get_token_from_header(authorization: str = Header(...)):
    if authorization.startswith("Bearer "):
        return authorization[7:]
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")