from typing import List
import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from wrapperfunction.admin.integration.aisearch_connector import delete_indexed_data
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings
from wrapperfunction.admin.service import crawl_service
from wrapperfunction.core.config import OPENAI_API_VERSION, SEARCH_ENDPOINT, SEARCH_KEY
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode


def crawling(
    urls: List[CrawlRequestUrls],
    settings: CrawlSettings,
):
    return crawl_service.crawl_urls(urls, settings)


def delete_indexes(index_name: str, key: str, value):
    try:
        delete_indexed_data(index_name, key, value)
        return JSONResponse(
            content={"message": f"index '{index_name} deleted successfully."},
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Blob not found")
    
async def resetIndexer(name: str):
    try:
        url = f"{SEARCH_ENDPOINT}/indexers/{name}/reset?api-version={OPENAI_API_VERSION}"
        headers = {
            "Content-Type": "application/json",
            "api-key": SEARCH_KEY
        }
        requests.post(url=url,headers=headers)
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            message=f"{name} Indexer Reseted Successfuly", 
                            ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def runIndexer(name: str):
    try:
        url = f"{SEARCH_ENDPOINT}/indexers/{name}/run?api-version={OPENAI_API_VERSION}"
        headers = {
            "Content-Type": "application/json",
            "api-key": SEARCH_KEY
        }
        requests.post(url=url,headers=headers)
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            message=f"{name} Indexer Is Running Successfully", 
                            ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
