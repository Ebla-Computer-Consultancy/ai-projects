
from fastapi import HTTPException , File, Form
from fastapi.responses import JSONResponse
import json

from wrapperfunction.admin.integration.crawl_integration import delete_base_on_subfolder, delete_blobs_base_on_metadata, edit_blob_by_new_jsonfile, process_and_upload, run_crawler, transcript_pdfs
from wrapperfunction.chatbot.integration.openai_connector import chat_completion
from wrapperfunction.search.integration.aisearch_connector import search_query

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
    
async def media_search(search_text: str):
    try:
        res = search_query(search_text=search_text, search_index="rera-media-test")
        top_3 = res["rs"]
        top_3_chunks = [answer["chunk"] for answer in top_3]
        
        chat_res=chat_completion(
            system_message="you are an assistant and expert in writing reports that write long reports from a given results",
            user_message=f"write a long report from this results in about 2 pages(reach the max).. search_results:{top_3_chunks},search_text:{search_text}",
            max_tokens=4000
            )
        
        # file = open(f"report.docx", "a", encoding="utf-8")        
        # file.write(chat_res["message"]["content"])
        # file.close()
        return JSONResponse(content={"message":chat_res["message"]["content"],"search_results":top_3_chunks}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def media_crawl(topic: str, url: str):
    try:
        #1 get data
        
        #2 save to blob storage
        
        #3 run the indexer
        return JSONResponse(content={"msg": "crawling"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    