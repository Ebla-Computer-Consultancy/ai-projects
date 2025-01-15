from fastapi import APIRouter
import wrapperfunction.speech.service.speech_service  as speech_service

router = APIRouter()

@router.get("/token")
def get_speech_token():
    return speech_service.get_speech_token()

@router.get("/fetch-access-info")
def get_speech_endpoint_and_key():
    return speech_service.get_speech_endpoint_and_key()
