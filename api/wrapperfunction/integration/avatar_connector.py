from fastapi import HTTPException
import requests
from wrapperfunction.common.model.service_return import ServiceReturn, StatusCode
import wrapperfunction.core.config as config

def get_headers():
    return {
        "Authorization": f"Bearer {config.AVATAR_AUTH_KEY}",
        "Content-Type": "application/json",
    }


def start_stream(stream_id: str):
    data= { "avatarCode": config.AVATAR_CODE,
            "voiceId": config.AVATAR_VOICE_ID,
            "voiceProvider": config.AVATAR_VOICE_PROVIDER
        }
   
    if stream_id:
        response = requests.get(f"{config.AVATAR_API_URL}/streams/{stream_id}", headers=get_headers())
        stream = response.json()
        if not stream.get("id"):
            stream_id = None

    if not stream_id:
        response = requests.post(f"{config.AVATAR_API_URL}/streams", headers=get_headers(), json=data)
        stream = response.json()
        if not stream.get("id"):
            raise HTTPException(status_code=500, detail="Failed to start stream")
        
    return ServiceReturn(status=StatusCode.SUCCESS, message="stream created successfully",data=stream).to_dict()
 

def send_candidate(stream_id: str,jsonData: dict):
    response = requests.post(f"{config.AVATAR_API_URL}/streams/candidate/{stream_id}", headers=get_headers(), json=jsonData)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to send candidate")
    return ServiceReturn(status=StatusCode.SUCCESS, message="Candidate sent successfully").to_dict()


def send_answer(stream_id: str,jsonData: dict):
    response = requests.put(f"{config.AVATAR_API_URL}/streams/{stream_id}", headers=get_headers(), json=jsonData)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to send answer")
    return ServiceReturn(status=StatusCode.SUCCESS, message="Answer sent successfully").to_dict()


def render_text(stream_id: str,text: str):
    response = requests.post(f"{config.AVATAR_API_URL}/streams/render/{stream_id}", headers=get_headers(), json={"text": text})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to render text")
    return ServiceReturn(status=StatusCode.SUCCESS, message="Text rendered successfully").to_dict()


def close_stream(stream_id: str):
    response = requests.delete(f"{config.AVATAR_API_URL}/streams/{stream_id}", headers=get_headers())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to close stream")
    return ServiceReturn(status=StatusCode.SUCCESS, message="Stream closed successfully").to_dict()
