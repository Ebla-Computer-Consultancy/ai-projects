from wrapperfunction.admin.integration.blob_storage_integration import get_blob_client,get_container_client
from wrapperfunction.admin.integration.skills_connector import inline_read_scanned_pdf
from azure.storage.blob import BlobType, BlobBlock,BlobServiceClient
import urllib.parse
from wrapperfunction.core import config
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from urllib.parse import unquote
import json
import os


def get_blobs_name(container_name: str, subfolder_name: str= None):
    _ , blob_list = get_container_client(container_name = container_name, subfolder_name= subfolder_name)
    blobs = [blob.name for blob in blob_list]
    return {"blobs": blobs}

async def add_blobs(container_name, subfolder_name, metadata_1, metadata_2, metadata_4, files):
    for file in files:
        contents = await file.read()
        data = json.dumps(contents.decode('utf-8'))
        append_blob(blob_name= file.filename,
                    blob=data,
                    container_name=container_name,
                    folder_name = subfolder_name,
                    metadata_1 = metadata_1,
                    metadata_2= metadata_2,
                    metadata_3= "notcrawled",
                    metadata_4= metadata_4)
    return JSONResponse(
            content={
                "message": f"files have been uploaded successfully"
            },
            status_code=200,
        )


def append_blob(
    blob_name: str,
    blob: str,
    container_name=config.BLOB_CONTAINER_NAME,
    folder_name: str = config.SUBFOLDER_NAME,
    metadata_1=None,
    metadata_2=None,
    metadata_3="crawled",
    metadata_4=None,
):
    blob_client = get_blob_client(container_name, blob_name=f"{folder_name}/{blob_name}")
    if metadata_3 == "crawled":
        blob_client.upload_blob(blob, blob_type=BlobType.AppendBlob, overwrite=True)
    else:
        blob_client.upload_blob(blob, overwrite=True)

    encoded_url = urllib.parse.quote(metadata_2)
    if metadata_4 == "link":
        encoded_url = urllib.parse.unquote(encoded_url)
    if metadata_1 is not None and metadata_2 is not None:
        blob_metadata = blob_client.get_blob_properties().metadata or {}
        more_blob_metadata = {
            "website_url": metadata_1,
            "ref_url": encoded_url,
            "indexing_type": metadata_3,
            "type": metadata_4,
        }
        blob_metadata.update(more_blob_metadata)

    # Set metadata on the blob
    blob_client.set_blob_metadata(metadata=blob_metadata)

async def delete_blob_by_metadata(metadata_key, metadata_value):
    if not metadata_key or not metadata_value:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        print(metadata_value)
        metadata_value_ = unquote(metadata_value)
        print(metadata_value_)
        delete_blobs(metadata_key=metadata_key, metadata_value=metadata_value)
        return JSONResponse(
            content={
                "message": f"Blob with metadata {metadata_key}={metadata_value} deleted successfully"
            },
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Blob not found")

async def delete_blob_by_list_of_title(blobs_name_list:list,subfolder_name:str, container_name:str):
    if not blobs_name_list:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        delete_blobs(blobs_name_list= blobs_name_list,subfolder_name=subfolder_name, container_name=container_name)
        return JSONResponse(
            content={
                "message": f"Blob from the Blob list had been deleted successfully"
            },
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Blob not found")

async def delete_subfolder(container_name, subfolder_name):
    if not container_name or not subfolder_name:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        print(container_name)
        print(subfolder_name)
        delete_blobs(container_name=container_name, subfolder_name=subfolder_name)
        return JSONResponse(
            content={
                "message": f"Subfolder '{subfolder_name}' in the container {container_name} deleted successfully."
            },
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Subfolder not found")

def delete_blobs(
    metadata_key=None,
    metadata_value=None,
    blobs_name_list= None,
    subfolder_name="jsondata",
    container_name="test1"
):
    container_client, blobs = get_container_client(
        subfolder_name= subfolder_name,
        container_name= container_name
    )
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        blob_metadata = blob_client.get_blob_properties().metadata
        blob_name = blob_client.get_blob_properties().name.split("/")[1]
        if metadata_key is not None:
            if blob_metadata.get(metadata_key) == metadata_value or unquote(blob_metadata.get(metadata_key)) == metadata_value:
                blob_client.delete_blob()
        elif blobs_name_list is not None:
            if blob_name in blobs_name_list:
                blob_client.delete_blob()
        else:
            blob_client.delete_blob()

def edit_blob_by_new_jsonfile(
    metadata_key,
    metadata_value,
    new_content,
    subfolder_name="jsondata",
):
    container_client, blobs = get_container_client(
        subfolder_name = subfolder_name
    )

    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        # print(blob)
        blob_metadata = blob_client.get_blob_properties().metadata
        if blob_metadata.get(metadata_key) == metadata_value:
            # Download the existing blob content
            blob_data = blob_client.download_blob().readall()
            blob_content = json.loads(blob_data)
            # Edit the blob content
            blob_content.update(new_content)
            blob_metadata.update(blob_metadata)

            # Upload the updated content back to the blob
            blob_client.upload_blob(json.dumps(blob_content), overwrite=True)
            blob_client.set_blob_metadata(metadata=blob_metadata)
            return JSONResponse(
                content={
                    "message": f"Blob with metadata {metadata_key}={metadata_value} edited successfully"
                },
                status_code=200,
            )
    return HTTPException(status_code=404, detail="Blob not found")

def edit_blob(new_content_file, metadata_key, metadata_value):
    try:
        new_content = json.load(new_content_file.file)  #
        new_content_file.file.seek(0)
        print(new_content_file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read new content file: {str(e)}"
        )
    edit_blob_by_new_jsonfile(metadata_key, metadata_value, new_content)

def upload_files_to_blob(folder_path: str, subfolder_name="jsondata"):
        # Initialize the BlobServiceClient
        # blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
        # Get the container client
        container_client =  get_container_client(subfolder_name = subfolder_name)
        # blob_service_client.get_container_client(container_name = container_name)
    
        # Iterate over all files in the specified folder
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                # Construct the full file path
                file_path = os.path.join(root, file_name)
            
                # Construct the blob path
                blob_path = f'{subfolder_name}/{file_name}'
            
                # Get the blob client
                blob_client = container_client.get_blob_client(blob=blob_path)
                # Open the file in binary mode
                with open(file_path, 'rb') as data:
                    file_size = os.path.getsize(file_path)
                    chunk_size = 4 * 1024 * 1024  # 4MB
                    blocks = []
                    block_id = 0
                
                    while True:
                        chunk = data.read(chunk_size)
                        if not chunk:
                            break
                        block_id_str = f'{block_id:06d}'
                        blob_client.stage_block(block_id_str, chunk)
                        blocks.append(BlobBlock(block_id=block_id_str))
                        block_id += 1
                
                blob_client.commit_block_list(blocks)

def update_json_with_pdf_text(json_file, folder_path):
    with open(json_file, "r", encoding="utf8") as file:
        data = json.load(file)
    for item in data:
        if "pdf_url" in item:
            item["url"] = item.pop("pdf_url")
            pdf_filename = item["title"]
            pdf_path = folder_path + "/" + pdf_filename
            # Extract text from the PDF
            extracted_text = inline_read_scanned_pdf(pdf_path)
            # Append the extracted text to the JSON item
            item["body"] = extracted_text

    # Save the updated JSON back to the file
    with open("updated_" + json_file[2:], "w", encoding="utf8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)