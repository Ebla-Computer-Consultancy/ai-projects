from fastapi import APIRouter, Depends, HTTPException, Request, status
from wrapperfunction.function_auth.service import jwt_service
from wrapperfunction.function_auth.service import auth_service
from wrapperfunction.function_auth.model.func_auth_model import LoginRequest, User
from wrapperfunction.function_auth.service import table_service

router = APIRouter()

@router.post("/login")
async def login(body: LoginRequest):
    try:
        response = auth_service.get_jwt(username=body.username, password=body.password)
        return response 
    except Exception as e:
        raise e

async def hasAuthority(request: Request, token: str = Depends(jwt_service.get_token_from_header)):
    try:
        permission = auth_service.set_permission(request.url)
        payloads = jwt_service.decode_jwt(token)
        user = User(username=payloads["name"],enc_password=payloads["enc_password"],permissions=payloads["permissions"])
        if payloads["token_type"] == "refresh":
            if len(table_service.get_user_by_token(token=token, username=user.username)) < 1:
                raise HTTPException(status_code=401, detail=f"Invalid refresh_token")
        have_permission = False
        for per in user.permissions:
            if per["name"] == permission:
                have_permission = True
                break
        if not have_permission:    
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User don't have required permission to access this endpoint")
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized: {str(e)}")
    