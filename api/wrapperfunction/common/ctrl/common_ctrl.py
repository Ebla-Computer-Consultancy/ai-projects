
from fastapi import APIRouter, Request, UploadFile
import wrapperfunction.common.service.common_service as commonservice

router = APIRouter()

@router.post("/speech/transcribe/")
async def transcribe(file: UploadFile):
    return await commonservice.transcribe(file)

@router.post("/avatar/start-stream/")
def start_stream(stream_id: str = None):
    return commonservice.start_stream(stream_id)

@router.post("/avatar/send-candidate/{stream_id}")
async def send_candidate(stream_id: str,request: Request):
    return await commonservice.send_candidate(stream_id,request)

@router.put("/avatar/send-answer/{stream_id}")
async def send_answer(stream_id: str,request: Request):
    return await commonservice.send_answer(stream_id,request)

@router.post("/avatar/render-text/{stream_id}")
async def render_text(stream_id: str,request: Request):
    return await commonservice.render_text(stream_id,request)

@router.delete("/avatar/close-stream/{stream_id}")
def close_stream(stream_id: str):
    return commonservice.close_stream(stream_id)