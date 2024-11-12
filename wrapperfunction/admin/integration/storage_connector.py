from io import BytesIO
import os
from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException, UploadFile


async def upload_to_blob_container(
    file: UploadFile, connection_string: str, container_name: str, voice_name: str
):
    try:
        service_client = BlobServiceClient.from_connection_string(connection_string)

        container_client = service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
        file_bytes = await file.read()
        with BytesIO(file_bytes) as byte_stream:
            container_client.upload_blob(name=f"{voice_name}", data=byte_stream)
    except Exception as e:
        return HTTPException(400, "Something went wrong")
    return f"https://rerastorage01.blob.core.windows.net/stt-voices/{voice_name}"


def download_blob_from_container(
    connection_string: str,
    container_name: str,
    download_file_path: str,
    voice_name: str,
):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=voice_name
    )

    with open(download_file_path, "wb+") as download_file:
        download_file.write(blob_client.download_blob().readall())
        download_file.close()


def delete_blob(connection_string: str, container_name: str, blob_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )
    blob_client.delete_blob()


def delete_blob_snapshots(connection_string: str, container_name: str, blob_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )
    blob_client.delete_blob(delete_snapshots="include")

def upload_file_to_azure(file_path, container_name, blob_name, connection_string):
    with open(file_path, "rb") as data:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data)
        print(f"Uploaded {file_path} to {blob_name}")
           
def push_To_Container(folder, connection_string, container_name):
    for root, dirs, files in os.walk(folder):
        for file in files:
            local_file_path = os.path.join(root, file)
                
            relative_path = os.path.relpath(local_file_path, folder)
            blob_name = relative_path.replace("\\", "/") 

            upload_file_to_azure(local_file_path, container_name, blob_name, connection_string)
