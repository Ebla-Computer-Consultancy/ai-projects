
from fastapi import APIRouter, HTTPException, Request,UploadFile
from wrapperfunction.video_indexer.service import vi_service
from wrapperfunction.video_indexer.model import vi_model

router = APIRouter()

@router.post("/create_vi")
async def create_vi(virequest: vi_model.VIRequest, request: Request):
    try:
        return await vi_service.create_video_index(v_name=virequest.video_name,v_url=virequest.video_url,request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_vi")
async def get_vi(vid: str):
    try:
        return await vi_service.get_video_index(v_id= vid)
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

# @router.get("/get_token")
# async def get_token():
#     try:
#         return vi_service.get_access_token()
#     except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/upload_video")
async def upload_video(file: UploadFile,request: Request):
    try:
        return await vi_service.upload_video(video_file=file,request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    