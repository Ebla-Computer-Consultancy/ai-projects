from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from wrapperfunction.core import config
from wrapperfunction.function_auth.service import jwt_service
from wrapperfunction.function_auth.service import auth_service

router = APIRouter()
    
@router.post("/login")
def login(body: OAuth2PasswordRequestForm = Depends()):
    try:
        response = auth_service.authenticate_user(username=body.username, password=body.password)
        return response 
    except Exception as e:
        raise e

@router.get("/refresh-token")
async def update_refresh_token(token: str = Depends(jwt_service.get_token_from_header)):
    try:
        return auth_service.update_refresh_token(token=token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized: {str(e)}")    

def hasAuthority(permission: str):
    if config.AUTH_ENABLED:
        async def dependency(request: Request, token: str = Depends(jwt_service.get_token_from_header)):
            try:
                auth_service.hasAnyAuthority(request=request, token=token, permission=permission)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized: {str(e)}")
        return dependency
    else:
        async def dependency():
            return True
        return dependency
    