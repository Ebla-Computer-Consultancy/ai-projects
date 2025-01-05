from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta
from typing import Tuple
from wrapperfunction.core import config
from wrapperfunction.function_auth.model.func_auth_model import User

# Function to create JWT tokens
def generate_jwt_tokens(user: User) -> Tuple[str, str]:
    try:
        # Current time
        now = datetime.utcnow()

        # Create Access Token (1-hour expiration)
        access_token = jwt.encode(
            payload = {
                "sub": user.username,
                "permissions": user.permissions,
                "enc_password": user.enc_password, 
                "exp": now + timedelta(hours=1) 
            },
            key = config.JWT_SECRET_KEY,
            algorithm=config.ALGORITHM
        )

        # Create Refresh Token (24-hour expiration)
        refresh_token = jwt.encode(
            payload = {
                "sub": user.username,
                "permissions": user.permissions,
                "enc_password": user.enc_password, 
                "exp": now + timedelta(hours=24)  # Refresh token expires in 24 hours
            },
            key = config.JWT_SECRET_KEY,
            algorithm = config.ALGORITHM
        )

        return access_token, refresh_token
    except Exception as e:
        raise Exception("Error While Generating Tokens")
# Function to decode and verify JWT tokens
def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Unauthorized: Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")