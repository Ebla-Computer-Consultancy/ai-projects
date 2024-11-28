
from typing import List
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from wrapperfunction.admin.model.indexer_model import IndexerRequest,IndexInfo
import wrapperfunction.admin.service.admin_service as admin_service
import wrapperfunction.admin.service.blob_service as blob_service
from fastapi import HTTPException


router = APIRouter()

@router.post("/add_json_blobs/")
async def add_blobs(container_name: str, subfolder_name: str, metadata_1: str, metadata_2: str, metadata_4: str, files: list[UploadFile] = File()):
    try:
        # Read the content of the file
        return await blob_service.add_blobs(container_name, subfolder_name, metadata_1, metadata_2, metadata_4, files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_blobs/{container_name}")
async def get_blobs(container_name: str):
    try:
        return blob_service.get_blobs_name(container_name=container_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_blobs/{container_name}/{subfolder_name}")
async def get_blobs(container_name: str, subfolder_name: str):
    try:
        return blob_service.get_blobs_name(container_name, subfolder_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_subfolder")
async def delete_subfolder(container_name: str, subfolder_name: str):
    try:
        return await blob_service.delete_subfolder(container_name, subfolder_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_blob_by_metadata")
async def delete_blob_by_metadata(metadata_key: str, metadata_value: str):
    try:
        return await blob_service.delete_blob_by_metadata(metadata_key, metadata_value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_blob_by_list_of_titles")
async def delete_blob_by_list_of_titles(blobs_name_list: list[str],subfolder_name:str, container_name:str): # not working
    try:
        return await blob_service.delete_blob_by_list_of_title(blobs_name_list = blobs_name_list,subfolder_name=subfolder_name, container_name=container_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reset_index/{index_name}")
async def reset_index(index_name: str):
    try:
        return admin_service.reset_index(index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset_index/{index_name}/{value}/{key}")
async def reset_index(index_name: str, value: str, key: str = "chunk_id"):
    try:
        return admin_service.delete_indexes(index_name, key, value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run_index/{index_name}")
async def run_index(index_name: str):
    try:
        return admin_service.run_index(index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_pdfs/")
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

@router.get("/index-info/{index_name}", response_model=IndexInfo)
async def index_info(index_name: str):
    try:
        return admin_service.index_info(index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

