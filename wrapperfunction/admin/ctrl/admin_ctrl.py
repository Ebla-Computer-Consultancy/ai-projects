from fastapi import APIRouter, HTTPException, Request
import wrapperfunction.admin.service.admin_service as adminservice
from fastapi import HTTPException , File, Form
# import wrapperfunction.admin.model.crawl_model as CrawlRequest

router = APIRouter()

@router.post("/crawl/")
async def crawl(request: Request):
    try:
        return adminservice.crawl(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape")
async def scrape(file_path: str, container_name:str):
    try:
        return adminservice.scrape(file_path,container_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_subfolder")
async def delete_subfolder(container_name:str, subfolder_name:str):
    try:
        return await adminservice.delete_subfolder(container_name, subfolder_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_blob")
async def delete_blob(metadata_key:str,metadata_value:str):
    try:
        return await adminservice.delete_blob(metadata_key,metadata_value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/reset_index")
async def reset_index(index_name: str):
    try:
        return adminservice.delete_indexes(index_name,key ="chunk_id", value = None )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reset_index")
async def reset_index(index_name: str, value:str, key:str ="chunk_id"):
    try:
        return adminservice.delete_indexes(index_name,key,value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# @router.post("/edit_blob/")
# async def edit_blob(metadata_key: str, metadata_value: str,
#                     new_content_file: UploadFile = File()):
#     try:
#         # Read the content of the file
#         return adminservice.edit_blob(new_content_file,metadata_key,metadata_value)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.post("/add_pdfs/")
# async def add_pdfs(request: Request):
#     try:
#         return await adminservice.add_pdfs()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))