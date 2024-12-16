from fastapi import APIRouter, HTTPException, UploadFile
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings
from wrapperfunction.admin.model.indexer_model import IndexInfo, IndexerRequest
from wrapperfunction.admin.service import blob_service
from wrapperfunction.admin.service.crawl_service import crawl_urls
from wrapperfunction.search.service import search_service


router = APIRouter()

@router.post("/crawler/")
def crawler(urls: list[CrawlRequestUrls], settings: CrawlSettings = None):
    try:
        # Read the content of the file
        return crawl_urls(urls, settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_blobs/")
def upload_blobs(container_name: str, subfolder_name: str, metadata_1: str, metadata_2: str, metadata_4: str, files: list[UploadFile]):
    try:
        json_files=[]
        pdf_files=[]
        for file in files:
            if file.content_type == "application/pdf":
                pdf_files.append(file)
            else:
                json_files.append(file)
        blob_service.read_and_upload_pdfs(pdf_files, container_name, store_pdf_subfolder=subfolder_name+"_pdf",subfolder_name= subfolder_name)
        blob_service.add_blobs(container_name, subfolder_name, metadata_1, metadata_2, metadata_4, json_files)
        return {"message": "Files uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_blobs/{container_name}")
def get_blobs(container_name: str, subfolder_name: str = None):
    try:
        return blob_service.get_blobs_name(container_name=container_name, subfolder_name=subfolder_name)
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

@router.post("/reset_index/{index_name}")
async def reset_index(index_name: str):
    try:
        return search_service.reset_index(index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset_index/{index_name}/{value}/{key}")
async def reset_index(index_name: str, value: str, key: str = "chunk_id"):
    try:
        return search_service.delete_indexes(index_name, key="chunk_id", value=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-indexer/")
async def resetIndexer(request: IndexerRequest):
    try:
        return await search_service.resetIndexer(request.index_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run_indexer/{index_name}")
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

