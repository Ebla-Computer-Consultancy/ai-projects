from fastapi import APIRouter, HTTPException
from wrapperfunction.core.model.customskill_model import CustomSkillRequest
from wrapperfunction.media_monitoring.model.media_crawl_model import MediaCrawlRequest
from wrapperfunction.media_monitoring.model.media_model import MediaRequest
from wrapperfunction.media_monitoring.service import media_service

router = APIRouter()

@router.post("/generate-report/")
async def generate_report(request:MediaRequest):
    try:
        return await media_service.generate_report(request.search_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl/")
async def media_crawl(request:MediaCrawlRequest):
    try:
        return await media_service.media_crawl(request.urls, request.settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment/")   
async def sentiment(request:CustomSkillRequest):
    try:
        return await media_service.sentiment_skill(values=request.values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-language/")   
async def detect_language(request:CustomSkillRequest):
    try:
        return await media_service.detect_language_skill(values=request.values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/key-phrases/")   
async def key_phrases(request:CustomSkillRequest):
    try:
        return await media_service.extract_key_phrases_skill(values=request.values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/entity-recognition/")   
async def entity_recognition(request:CustomSkillRequest):
    try:
        return await media_service.entity_recognition_skill(values=request.values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image-analysis/")   
async def image_analysis(request:CustomSkillRequest):
    try:
        return await media_service.image_analysis_skill(values=request.values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image-embedding/")   
async def image_embedding(request:CustomSkillRequest):
    try:
        return await media_service.image_embedding_skill(values=request.values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
