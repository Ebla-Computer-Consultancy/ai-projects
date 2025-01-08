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

@router.post("/update-refresh-token")
async def update_refresh_token(token: str = Depends(jwt_service.get_token_from_header)):
    try:
        return auth_service.update_refresh_token(token=token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized: {str(e)}")    

async def hasAuthority(request: Request, token: str = Depends(jwt_service.get_token_from_header)):
    try:
        auth_service.hasAnyAuthority(request=request, token=token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized: {str(e)}")
    