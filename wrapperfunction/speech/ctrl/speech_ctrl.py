from fastapi import APIRouter
import wrapperfunction.speech.service.speech_service  as speech_service

router = APIRouter()

@router.get("/token")
def get_speech_token():
    return speech_service.get_speech_token()

@router.get("/authorization-access-token")
def get_speech_authorization_access_token():
    return speech_service.get_speech_authorization_access_token()