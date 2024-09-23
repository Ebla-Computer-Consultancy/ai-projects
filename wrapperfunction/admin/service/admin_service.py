from wrapperfunction.integration.crawl_integration import run_crawler, process_and_upload, upload_files_to_blob,delete_blobs_base_on_metadata, delete_base_on_subfolder, edit_blob_by_new_jsonfile,transcript_pdfs
from fastapi import HTTPException , UploadFile, File, Form
from fastapi.responses import JSONResponse
import json
import codecs

def crawl(request):
    link = request.query_params.get('link')
    docs_flag = False
    if not link:
        raise ValueError("Missing link parameter")

    filepath, filename = run_crawler(link)
    # if docs_flag:
    #     upload_files_to_blob(folder_path = "./export/docs/"+filename[:-5])
    process_and_upload(filepath, link)

    return {"message": "Crawling completed successfully"}

async def delete_blob(request):
    metadata_key = request.query_params.get('metadata_key')
    metadata_value = request.query_params.get('metadata_value')

    if not metadata_key or not metadata_value:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        delete_blobs_base_on_metadata(metadata_key,metadata_value)
        return JSONResponse(content={"message": f"Blob with metadata {metadata_key}={metadata_value} deleted successfully"}, status_code=200)
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
        delete_base_on_subfolder(subfolder_name,container_name)
        return JSONResponse(content={"message": f"Subfolder '{subfolder_name}' in the container {container_name} deleted successfully."}, status_code=200)
    except:
        raise HTTPException(status_code=404, detail="Subfolder not found")

def edit_blob(new_content_file,metadata_key,metadata_value):
    # metadata_key: str = Form(request)
    # metadata_value: str = Form(request)
    # new_content_file: UploadFile = File(request)

    try:
        new_content = json.load(new_content_file.file)#
        new_content_file.file.seek(0)
        print(new_content_file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read new content file: {str(e)}")
    edit_blob_by_new_jsonfile(metadata_key,metadata_value,new_content)
    
async def add_pdfs():
    try:
        transcript_pdfs()
        return JSONResponse(content={"message": f"done"}, status_code=200)
    except:
        raise HTTPException(status_code=404, detail="Blob not found")