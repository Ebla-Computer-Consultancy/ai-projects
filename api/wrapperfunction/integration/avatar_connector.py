from fastapi import HTTPException
import requests
from wrapperfunction.common.model.service_return import ServiceReturn, StatusCode
import wrapperfunction.core.config as config
import re
from num2words import num2words

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
    print(f"Rendering text on stream: {stream_id}")
    try:
        response = requests.post(f"{config.AVATAR_API_URL}/streams/render/{stream_id}", headers=get_headers(), json={"text": text})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to render text")
        print("Text rendered successfully")
        return ServiceReturn(status=StatusCode.SUCCESS, message="Text rendered successfully").to_dict()
    except Exception as error:
        print(f"Failed to render text: {str(error)}")
        raise

async def render_text_async(stream_id: str,text: str,is_ar: bool):
        render_text(stream_id,clean_text(text,is_ar))

def close_stream(stream_id: str):
    response = requests.delete(f"{config.AVATAR_API_URL}/streams/{stream_id}", headers=get_headers())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to close stream")
    return ServiceReturn(status=StatusCode.SUCCESS, message="Stream closed successfully").to_dict()


def clean_text(text: str,is_ar: bool = False):
    # Remove any pattern like [doc*], where * represents numbers
    # Remove non-readable characters (anything not a letter, number, punctuation, or whitespace)
    # text = re.sub(r'[^\w\s,.!?\'\"-]', '', text)
    text = re.sub(r'<[^>]*>|\[doc\d+\]', '', text)
    if is_ar:
        text = replace_numbers_with_words(text)
    return text

def replace_number(match):
        number = match.group(0)
        number = number.replace(',', '')
        return num2words(int(number), lang='ar')

def replace_numbers_with_words(phrase):
    digit_pattern = r'[\u0660-\u0669\u0030-\u0039]+(?:,[\u0660-\u0669\u0030-\u0039]+)*'
    phrase = re.sub(digit_pattern, replace_number, phrase)
    return phrase

