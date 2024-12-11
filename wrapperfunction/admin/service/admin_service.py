import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from wrapperfunction.core.config import OPENAI_API_VERSION, SEARCH_ENDPOINT, SEARCH_KEY
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from wrapperfunction.search.integration.aisearch_connector import delete_indexed_data, get_index_info, reset_indexed_data, run_indexer

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
                            message=f"{name} Indexer Reset Successfully", 
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

def reset_index(index_name: str):
    try:
        reset_indexed_data(index_name)
        return JSONResponse(content={"message": f"index '{index_name} deleted successfully."}, status_code=200)
    except:
        raise HTTPException(status_code=404, detail="index not found")

def run_index(index_name: str):
    try:
        run_indexer(index_name)
        return JSONResponse(content={"message": f"index '{index_name} reloaded successfully."}, status_code=200)
    except:
        raise HTTPException(status_code=404, detail="index not found")

def index_info(index_name: str):
    try:
        return get_index_info(index_name)
    except:
        raise HTTPException(status_code=404, detail="index not found")

