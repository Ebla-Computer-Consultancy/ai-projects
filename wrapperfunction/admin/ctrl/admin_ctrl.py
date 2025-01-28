from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, UploadFile
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings
from wrapperfunction.admin.service import blob_service
from wrapperfunction.admin.service.crawl_service import crawl_urls
from wrapperfunction.core.service import settings_service
from wrapperfunction.function_auth.service import auth_db_service
from wrapperfunction.search.model.indexer_model import IndexInfo
from wrapperfunction.search.service import search_service
from wrapperfunction.core.utls.helper import pdfs_files_filter


router = APIRouter()

@router.post("/crawler/")
def crawler(urls: list[CrawlRequestUrls], settings: CrawlSettings = None):
    try:
        return crawl_urls(urls, settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-blobs/")
def upload_blobs(files: list[UploadFile], container_name: str, subfolder_name: str, metadata_1: str = None, metadata_2: str = None, metadata_4: str = "pdf"):
    try:
        pdf_files, json_files= pdfs_files_filter(files)
        blob_service.read_and_upload_pdfs(pdf_files, container_name, store_pdf_subfolder=subfolder_name+"_pdf",subfolder_name= subfolder_name)
        blob_service.add_blobs(container_name, subfolder_name, metadata_1, metadata_2, metadata_4, json_files)
        return {"message": "Files uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-blobs/{container_name}")
def get_blobs(container_name: str, subfolder_name: str = None):
    try:
        return blob_service.get_blobs_name(container_name=container_name, subfolder_name=subfolder_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-containers")
def get_containers():
    try:
        return blob_service.get_containers_name()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-subfolders/{container_name}")
def get_subfolders(container_name: str):
    try:
        return blob_service.get_subfolders_name(container_name=container_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-subfolder")
async def delete_subfolder(container_name: str, subfolder_name: str):
    try:
        return await blob_service.delete_subfolder(container_name, subfolder_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-blob-by-metadata")
async def delete_blob_by_metadata(metadata_key: str, metadata_value: str):
    try:
        return await blob_service.delete_blob_by_metadata(metadata_key, metadata_value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-blob-by-list-of-titles")
async def delete_blob_by_list_of_titles(blobs_name_list: list[str],subfolder_name:str, container_name:str): # not working
    try:
        return await blob_service.delete_blob_by_list_of_title(blobs_name_list = blobs_name_list,subfolder_name=subfolder_name, container_name=container_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/reset-index/{index_name}")
async def reset_index(index_name: str, value: str = None, key: str = "chunk_id"):
    try:
        if value is None:
            return search_service.reset_index(index_name)
        else:
            return search_service.delete_indexes(index_name, key=key, value=value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-indexer/{index_name}")
async def run_indexer(index_name: str):
    try:
        return search_service.run_indexer(index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index-info/{index_name}", response_model=IndexInfo)
async def index_info(index_name: str):
    try:
        return search_service.index_info(index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indexes-name")
async def indexes_name():
    try:
        return search_service.indexes_name()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))@router.get("/settings")

@router.get("/settings")    
async def get_all_settings():
    try:
        return settings_service.get_all_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings Error: {str(e)}")
    
@router.get("/settings/{entity_name}")
async def get_setting(entity_name: str):
    try:
        return settings_service.get_settings_by_entity(entity_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Settings Error: {str(e)}")

@router.post("/settings")
async def update_setting(entity: Dict[str, Any]):
    try:
        return settings_service.update_bot_settings(entity=entity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings Error: {str(e)}")
    
@router.put("/settings")
async def add_setting(body: Dict[str, Any]):
    try:
        return await settings_service.add_setting(entity=body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings Error: {str(e)}")

@router.delete("/settings")
async def delete_setting(body: dict):
    try:
        return settings_service.delete_bot_settings(entity=body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings Error: {str(e)}")

@router.post("/permission/update")
async def update_user_permissions(user_id: str, permissions_ids: List[str]):
    try:
        return await auth_db_service.update_user_permissions(user_id,permissions_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/permissions")
async def get_all_permissions():
    try:
        return auth_db_service.get_permissions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/permission/{id}")
async def get_permission(id: str):
    try:
        return auth_db_service.get_permission_by_id(id=id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_all_users():
    try:
        return auth_db_service.get_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{id}")
async def get_user(id: str):
    try:
        return auth_db_service.get_user_by_id(id=id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{id}/permissions")
async def get_user_permissions(id: str):
    try:
        return auth_db_service.get_full_user_permissions_info(user_id=id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user")
async def add_user(username: str):
    try:
        return await auth_db_service.add_user(username=username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user")
async def update_user(user: dict):
    try:
        return auth_db_service.update_user(user=user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user")
async def delete_user(user_id: str):
    try:
        return auth_db_service.delete_user(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sas-token") 
def get_sas_token(blob_url:str):
    try:
        return blob_service.generate_blob_sas_url(blob_url=blob_url)
    except Exception as e:    
        raise HTTPException(status_code=500, detail=str(e))    