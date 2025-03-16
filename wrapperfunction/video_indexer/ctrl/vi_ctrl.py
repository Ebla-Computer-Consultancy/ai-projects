
from fastapi import APIRouter, HTTPException, Request,UploadFile

from wrapperfunction.chat_history.service.chat_history_service import start_video_chat
from wrapperfunction.video_indexer.service import vi_service
from wrapperfunction.video_indexer.model import vi_model

router = APIRouter()
@router.get("/index")
async def get_video_index(vid: str, bot_name: str, language: str):
    try:
        return await vi_service.get_video_index(video_id=vid,bot_name=bot_name,language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/re-index")
async def reindex_video(request: vi_model.VIRequest):
    try:
        return await vi_service.reindex_video(v_id=request.video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/videos")
async def list_videos():
    try:
        return await vi_service.get_all_videos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_video(file: UploadFile,language: str):
    try:
        return await vi_service.upload_video(video_file=file,language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/start-video-chat")
async def Start_video_chat(video_id: str, request: Request,bot_name: str,language: str):
    try:
        return await start_video_chat(video_id=video_id, request=request,bot_name=bot_name,language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  


@router.post("/supported-languages")
def get_supported_languages():
    try:
        return vi_service.get_supported_languages()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))      