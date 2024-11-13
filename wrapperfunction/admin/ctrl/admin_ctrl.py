
from fastapi import APIRouter, HTTPException, Request
from wrapperfunction.admin.model.indexer_model import IndexerRequest
from wrapperfunction.admin.service import admin_service


router = APIRouter()


@router.post("/delete_subfolder")
async def delete_subfolder():
    try:
        return await admin_service.delete_blob(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_blob")
async def delete_blob(metadata_key: str, metadata_value: str):
    try:
        return await admin_service.delete_blob(metadata_key, metadata_value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset_index/{index_name}")
async def reset_index(index_name: str):
    try:
        return admin_service.delete_indexes(index_name, key="chunk_id", value=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset_index/{index_name}/{value}/{key}")
async def reset_index(index_name: str, value: str, key: str = "chunk_id"):
    try:
        return admin_service.delete_indexes(index_name, key, value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def add_pdfs(request: Request):
    try:
        return await admin_service.add_pdfs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/reset-indexer/")
async def resetIndexer(request: IndexerRequest):
    try:
        return await admin_service.resetIndexer(request.index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-indexer/")
async def runIndexer(request: IndexerRequest):
    try:
        return await admin_service.runIndexer(request.index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))