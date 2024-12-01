from fastapi import APIRouter, HTTPException

from wrapperfunction.video_indexer.service import vi_service
from wrapperfunction.video_indexer.model import vi_model

router = APIRouter()

@router.post("/create_vi")
async def create_vi(resquest: vi_model.VIRequest):
    try:
        return await vi_service.create_video_index(v_name=resquest.video_name,v_url=resquest.video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_vi")
async def get_vi(request: vi_model.VIRequest):
    try:
        return await vi_service.get_video_index(v_id= request.video_id)
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
        return await vi_service.get_all_video()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_token")
async def get_token():
    try:
        return vi_service.get_AccessToken()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))