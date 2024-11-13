import json
import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from wrapperfunction.admin.integration.aisearch_connector import delete_indexed_data
from wrapperfunction.admin.integration.crawl_integration import delete_base_on_subfolder, delete_blobs_base_on_metadata, edit_blob_by_new_jsonfile, process_and_upload, run_crawler, transcript_pdfs
from wrapperfunction.core.config import OPENAI_API_VERSION, OPENAI_CHAT_MODEL, RERA_STORAGE_CONNECTION, SEARCH_ENDPOINT, SEARCH_KEY
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode

def crawl(request):
    link = request.query_params.get("link")
    if not link:
        raise ValueError("Missing link parameter")

    filepath, filename = run_crawler(link) 
    # filepath = "./export_e7ce4d72-a094-48ef-958c-647e61e59d17.json"
    # split_json_file(filepath, filepath[:-5]+"-links.json", filepath[:-5]+"-docs.json")
    # download_pdfs(filepath[:-5]+"-docs.json", "./export/docs/"+filepath[2:-5])
    # update_json_with_pdf_text(filepath[:-5]+"-docs.json", "./export/docs/"+filepath[2:-5])
    # process_and_upload(filepath[:-5]+"-links.json","./export/", link)
    # process_and_upload("updated_"+filepath[2:-5]+"-docs.json","./export/docs/", link,True)
    return {"message": "Crawling completed successfully"}

async def delete_blob(metadata_key,metadata_value):
    if not metadata_key or not metadata_value:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        print(metadata_value)
        metadata_value_ = unquote(metadata_value)
        print(metadata_value_)
        delete_blobs_base_on_metadata(metadata_key, metadata_value)
        return JSONResponse(
            content={
                "message": f"Blob with metadata {metadata_key}={metadata_value} deleted successfully"
            },
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Blob not found")

async def delete_subfolder(request):
    container_name = request.query_params.get('container_name')
    subfolder_name = request.query_params.get('subfolder_name')

    if not container_name or not subfolder_name:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        print(container_name)
        print(subfolder_name)
        delete_base_on_subfolder(subfolder_name, container_name)
        return JSONResponse(
            content={
                "message": f"Subfolder '{subfolder_name}' in the container {container_name} deleted successfully."
            },
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Subfolder not found")


def edit_blob(new_content_file,metadata_key,metadata_value):
    try:
        new_content = json.load(new_content_file.file)  #
        new_content_file.file.seek(0)
        print(new_content_file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read new content file: {str(e)}")
    edit_blob_by_new_jsonfile(metadata_key,metadata_value,new_content)
    

def delete_indexes(index_name: str, key:str, value):
    try:
        delete_indexed_data(index_name, key, value)
        return JSONResponse(content={"message": f"index '{index_name} deleted successfully."}, status_code=200)
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
                            message=f"{name} Indexer Is Running Successfuly", 
                             ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
