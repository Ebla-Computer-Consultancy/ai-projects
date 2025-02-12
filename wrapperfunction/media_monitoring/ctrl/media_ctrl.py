from fastapi import APIRouter, HTTPException
from wrapperfunction.core.model.customskill_model import CustomSkillRequest
from wrapperfunction.media_monitoring.integration import x_integrations
from wrapperfunction.media_monitoring.model.media_crawl_model import MediaCrawlRequest
from wrapperfunction.media_monitoring.model.media_model import MediaRequest
from wrapperfunction.media_monitoring.model.x_model import XRequestModel
from wrapperfunction.media_monitoring.service import media_service

router = APIRouter()

@router.post("/generate-report/")
async def generate_report(request:MediaRequest):
    try:
        return await media_service.generate_report(request.search_text,
                                                   index_date_from=request.index_date_from,
                                                   index_date_to=request.index_date_to,
                                                   news_date_from=request.news_date_from,
                                                   news_date_to=request.news_date_to,
                                                   tags=request.tags)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl/")
async def media_crawl(request:MediaCrawlRequest):
    try:
        return await media_service.media_crawl(request.urls, request.settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawl/status")
async def get_all_urls_crawling_status():
    try:
        return media_service.get_crawling_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/x-search")
async def get_x_search_results(query: str, start_time: str = None, end_time: str = None, max_results: int = None):
    try:
        return x_integrations.x_search(query=query, start_time=start_time, end_time=end_time, max_results=max_results)
    except Exception as e:
        raise Exception(f"{str(e)}")

@router.put("/index/{index_name}")
async def update_index_with_skills(index_name:str):
    try:
        return await media_service.apply_skills_on_index(index_name)
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
