from fastapi import APIRouter, Request, UploadFile
from pydantic import BaseModel
import wrapperfunction.common.service.common_service as commonservice

router = APIRouter()


@router.post("/speech/transcribe")
async def transcribe(file: UploadFile):
    return await commonservice.transcribe(file)


@router.get("/speech/token")
def get_speech_token():
    return commonservice.get_speech_token()


@router.post("/avatar/start-stream")
def start_stream(size: str = 'half-size',stream_id: str = None):
    return commonservice.start_stream(size,stream_id)


@router.post("/avatar/send-candidate/{stream_id}")
async def send_candidate(stream_id: str, request: Request):
    return await commonservice.send_candidate(stream_id, request)


@router.put("/avatar/send-answer/{stream_id}")
async def send_answer(stream_id: str, request: Request):
    return await commonservice.send_answer(stream_id, request)


@router.post("/avatar/render-text/{stream_id}")
async def render_text(stream_id: str, request: Request):
    return await commonservice.render_text(stream_id, request)

@router.delete("/avatar/stop-render/{stream_id}")
def stop_render(stream_id: str):
    return commonservice.stop_render(stream_id)

@router.delete("/avatar/close-stream/{stream_id}")
def close_stream(stream_id: str):
    return commonservice.close_stream(stream_id)

@router.get("/get-chats/{user_id}")
def get_chats(user_id: str):
    return commonservice.get_all_chat_history(user_id)

class message(BaseModel):
    user_id: str
    content: str
    conversation_id: str
    Role: str
@router.post("/add-message/{message}")
async def add_message(message: message):
    return await commonservice.add_to_chat_history(message.user_id, message.content, message.conversation_id, message.Role)
@router.post("/start-chat/{user_id}")
async def start_chat(user_id: str):
    return await commonservice.start_chat(user_id)