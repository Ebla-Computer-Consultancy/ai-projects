from fastapi import APIRouter, HTTPException, Request
# import wrapperfunction.admin.service.admin_service as adminservice
from fastapi import HTTPException
from wrapperfunction.admin.model.crawl_model import IndexerRequest
from wrapperfunction.admin.service import admin_service

# import wrapperfunction.admin.model.crawl_model as CrawlRequest

router = APIRouter()

@router.post("/crawl/")
async def crawl(request: Request):
    try:
        return await admin_service.crawl(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_subfolder/")
async def delete_subfolder(request: Request):
    try:
        return await admin_service.delete_subfolder(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_blob/")
async def delete_blob(request: Request):
    try:
        return await admin_service.delete_blob(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/edit_blob/")
# async def edit_blob(metadata_key: str, metadata_value: str,
#                     new_content_file: UploadFile = File()):
#     try:
#         # Read the content of the file
#         return admin_service.edit_blob(new_content_file,metadata_key,metadata_value)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/add_pdfs/")
async def add_pdfs(request: Request):
    try:
        return await admin_service.add_pdfs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-indexer/")
async def resetIndexer(request: IndexerRequest):
    try:
        return await admin_service.resetIndexer(request.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-indexer/")
async def runIndexer(request: IndexerRequest):
    try:
        return await admin_service.runIndexer(request.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))