from wrapperfunction.admin.integration.blob_storage_integration import get_blob_client,get_container_client
from azure.storage.blob import BlobType,BlobBlock
import urllib.parse
from wrapperfunction.admin.model.crawl_settings import IndexingType
from wrapperfunction.core import config
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from urllib.parse import unquote
import json

from wrapperfunction.document_intelligence.service.document_intelligence_service import inline_read_scanned_pdf

def get_blobs_name(container_name: str, subfolder_name: str= "jsondata"):
    _ , blob_list = get_container_client(container_name = container_name, subfolder_name= subfolder_name)
    blobs = [blob.name for blob in blob_list]
    return {"blobs": blobs}

def add_blobs(container_name, subfolder_name, metadata_1, metadata_2, metadata_4, files: list[UploadFile]):
    for file in files:
        contents = file.read()

        data = json.dumps(json.loads(contents), ensure_ascii=False)
        append_blob(blob_name= file.filename,
                    blob= data,
                    container_name=container_name,
                    folder_name = subfolder_name,
                    metadata_1 = metadata_1,
                    metadata_2= metadata_2,
                    metadata_3= IndexingType.NOT_CRAWLED.value,
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
    folder_name: str = config.SUBFOLDER_NAME ,
    metadata_1=None,
    metadata_2=None,
    metadata_3: IndexingType = IndexingType.CRAWLED.value,
    metadata_4=None,
):
    blob_client = get_blob_client(container_name, blob_name=f"{folder_name}/{blob_name}")
    if metadata_3 == IndexingType.CRAWLED.value or metadata_3 == IndexingType.GENERATED.value:
        blob_client.upload_blob(blob, blob_type=BlobType.AppendBlob, overwrite=True)
    else:
        blob_client.upload_blob(blob, overwrite=True)

    blob_metadata = blob_client.get_blob_properties().metadata or {}
    if metadata_2 is not None:
        encoded_url = urllib.parse.quote(metadata_2)
    if metadata_4 == "link" and metadata_2 is not None:
        encoded_url = urllib.parse.unquote(encoded_url)
    if metadata_1 is not None and metadata_2 is not None:
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
        metadata_value_ = unquote(metadata_value)
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

def upload_files_to_blob(files: list,container_name :str, subfolder_name="pdfdata"):
        # Get the container client
        container_client, _ =  get_container_client(container_name = container_name,subfolder_name = subfolder_name)    
        for file in files:
                # Construct the blob path
                blob_path = f'{subfolder_name}/{file.filename}'
            
                # Get the blob client
                blob_client = container_client.get_blob_client(blob=blob_path)
                # Open the file in binary mode
                file_size = file.file._file.getbuffer().nbytes
                chunk_size = 4 * 1024 * 1024  # 4MB
                blocks = []
                block_id = 0
                
                while True:
                    chunk = file.file.read(chunk_size)
                    if not chunk:
                        break
                    block_id_str = f'{block_id:06d}'
                    blob_client.stage_block(block_id_str, chunk)
                    blocks.append(BlobBlock(block_id=block_id_str))
                    block_id += 1
                
                blob_client.commit_block_list(blocks)
                metadata_storage_path =blob_client.url
                return metadata_storage_path

def read_and_upload_pdfs(files,container_name,store_pdf_subfolder,subfolder_name):
    for file in files:
        filename = file.filename
        meta_url=upload_files_to_blob([file], container_name= container_name,subfolder_name= store_pdf_subfolder)
        file.file.seek(0)
        f = file.file.read()
        extracted_text = inline_read_scanned_pdf(file=None,file_bytes=f)

        data = {"ref_url":meta_url,"title":filename[:-4],"body":extracted_text}
        json_data = json.dumps(data, ensure_ascii=False)
        append_blob(blob_name= filename[:-4] + '.json',
                    blob=json_data,
                    container_name=container_name,
                    folder_name = subfolder_name,
                    metadata_1 = None,
                    metadata_2= None,
                    metadata_3= IndexingType.NOT_CRAWLED.value,
                    metadata_4= "pdf")
        print(f"Uploaded OCR results for {filename} to Azure Storage.")
