from fastapi import APIRouter, HTTPException 
from wrapperfunction.function_auth.service.ldap_service import get_jwt
from wrapperfunction.function_auth.model.func_auth_model import LoginRequest

router = APIRouter()

@router.post("/login")
async def login(body: LoginRequest):
    try:
        response = get_jwt(username=body.username, password=body.password)
        return response 
    except Exception as e:
        raise e