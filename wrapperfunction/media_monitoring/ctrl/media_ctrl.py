from fastapi import APIRouter, HTTPException, Request
from fastapi import HTTPException , File, Form
from wrapperfunction.admin.service import admin_service
from wrapperfunction.media_monitoring.model.media_model import MediaCrawlRequest, MediaRequest

router = APIRouter()

@router.post("/search")
async def media_search(request:MediaRequest):
    try:
        return await admin_service.media_search(request.search_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl")   
async def media_crawl(request:MediaCrawlRequest):
    try:
        return await admin_service.media_crawl(request.topics,request.urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
