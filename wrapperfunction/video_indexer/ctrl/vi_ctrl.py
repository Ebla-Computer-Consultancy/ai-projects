
from fastapi import APIRouter, HTTPException, Request,UploadFile
from wrapperfunction.video_indexer.service import vi_service
from wrapperfunction.video_indexer.model import vi_model

router = APIRouter()
@router.get("/get_vi")
async def get_vi(vid: str, request: Request):
    try:
        return await vi_service.get_video_index(v_id= vid, request= request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/reindex_video")
async def reindex_v(request: vi_model.VIRequest):
    try:
        return await vi_service.reindex_video(v_id= request.video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_all_videos")
async def get_all_vi():
    try:
        return await vi_service.get_all_videos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/upload_video")
async def upload_video(file: UploadFile,request: Request):
    try:
        return await vi_service.upload_video(video_file=file,request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
