from fastapi import HTTPException
import requests
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
import wrapperfunction.core.config as config
import wrapperfunction.core.utls.helper as helper


def get_headers():
    return {
        "Authorization": f"Bearer {config.AVATAR_AUTH_KEY}",
        "Content-Type": "application/json",
    }

#Stream

def start_stream(size: str,stream_id: str):
    avatar_code = config.AVATAR_CODE_FULL_SIZE if size=='life-size' else config.AVATAR_CODE
    data = {
        "avatarCode": avatar_code,
        "voiceId": config.AVATAR_VOICE_ID,
        "voiceProvider": config.AVATAR_VOICE_PROVIDER,
    }

    if stream_id:
        response = requests.get(
            f"{config.AVATAR_API_URL}/streams/{stream_id}", headers=get_headers()
        )
        stream = response.json()
        if not stream.get("id"):
            stream_id = None

    if not stream_id:
        response = requests.post(
            f"{config.AVATAR_API_URL}/streams", headers=get_headers(), json=data
        )
        stream = response.json()
        if not stream.get("id"):
            raise HTTPException(status_code=500, detail="Failed to start stream")

    return ServiceReturn(
        status=StatusCode.SUCCESS, message="stream created successfully", data=stream
    ).to_dict()


def send_candidate(stream_id: str, jsonData: dict):
    response = requests.post(
        f"{config.AVATAR_API_URL}/streams/candidate/{stream_id}",
        headers=get_headers(),
        json=jsonData,
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to send candidate"
        )
    return ServiceReturn(
        status=StatusCode.SUCCESS, message="Candidate sent successfully"
    ).to_dict()


def send_answer(stream_id: str, jsonData: dict):
    response = requests.put(
        f"{config.AVATAR_API_URL}/streams/{stream_id}",
        headers=get_headers(),
        json=jsonData,
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to send answer"
        )
    return ServiceReturn(
        status=StatusCode.SUCCESS, message="Answer sent successfully"
    ).to_dict()


def render_text(stream_id: str, text: str):
    print(f"Rendering text on stream: {stream_id}")
    try:
        response = requests.post(
            f"{config.AVATAR_API_URL}/streams/render/{stream_id}",
            headers=get_headers(),
            json={"text": text},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Failed to render text"
            )
        print("Text rendered successfully")
        return ServiceReturn(
            status=StatusCode.SUCCESS, message="Text rendered successfully"
        ).to_dict()
    except Exception as error:
        print(f"Failed to render text: {str(error)}")
        raise


async def render_text_async(stream_id: str, text: str, is_ar: bool):
    render_text(stream_id, helper.clean_text(text, is_ar))


def stop_render(stream_id: str):
    response = requests.delete(
       f"{config.AVATAR_API_URL}/streams/render/{stream_id}",
        headers=get_headers()
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to stop rendering text"
        )
    return ServiceReturn(
        status=StatusCode.SUCCESS, message="Text rendering stopped successfully"
    ).to_dict()

def close_stream(stream_id: str):
    response = requests.delete(
        f"{config.AVATAR_API_URL}/streams/{stream_id}", headers=get_headers()
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to close stream"
        )
    return ServiceReturn(
        status=StatusCode.SUCCESS, message="Stream closed successfully"
    ).to_dict()

#Video

def render_video(video_id: str):

    response = requests.post(
        f"{config.AVATAR_API_URL}/videos/render/{video_id}", headers=get_headers()
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail=response.reason
        )
    video = response.json()
    return ServiceReturn(
        status=StatusCode.SUCCESS, message="Render video successfully Done", data=video
        ).to_dict()


def retrieve_video(video_id: str):
    response = requests.get(
        f"{config.AVATAR_API_URL}/videos/{video_id}", headers=get_headers()
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail=response.reason
        )
    video = response.text
    return ServiceReturn(
        status=StatusCode.SUCCESS, message="Retrieve video successfully Done", data=video
        ).to_dict()
    
def list_videos(page: int=1, limit:int=50, with_deleted:bool= False):
    response = requests.get(
        f"{config.AVATAR_API_URL}/videos?page={page}&limit={limit}&deleted={with_deleted}", headers=get_headers()
                        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail=response.reason
        )
    list_of_videos = response.json()
    videos = list_of_videos["videos"]
    output_list = {video["name"] : video["_id"] for video in videos}
    return ServiceReturn(
        status=StatusCode.SUCCESS, message="List videos successfully Done", data=output_list
        ).to_dict()

def delete_video(video_id: str):
    response = requests.delete(
        f"{config.AVATAR_API_URL}/videos/{video_id}", headers=get_headers()
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail=response.reason
        )
    return ServiceReturn(
        status=StatusCode.SUCCESS, message=f"The video with ID: '{video_id}' has successfully Deleted"
        ).to_dict()