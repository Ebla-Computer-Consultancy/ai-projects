import datetime
from io import BytesIO
from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException, UploadFile
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from wrapperfunction.core import config


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

def upload_json_to_azure(content, container_name, blob_name, connection_string):
    print(f"\nUploading ... file\n")
    # Convert the text content to bytes
    content_bytes = content.encode("utf-8")

    # Create a blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Upload the content directly to Azure Blob
    blob_client.upload_blob(BytesIO(content_bytes), overwrite=True)
    print(f"\nUploaded content to {blob_name}\n")
    
def upload_pdf_to_azure(file_path: str, container_name: str, blob_name: str, connection_string: str):
    try:
        print(f"Uploading file '{file_path}' to Azure Blob Storage...")

        # Create the BlobServiceClient and BlobClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Upload the file directly from the local file system
        with open(file_path, "rb") as file:
            blob_client.upload_blob(file, blob_type="BlockBlob", overwrite=True)

        print(f"PDF uploaded successfully to blob: {blob_name} in container: {container_name}")

    except Exception as e:
        print(f"Failed to upload PDF: {str(e)}")

def generate_blob_sas_url(container_name: str, blob_name: str, connection_string: str, expiration_minutes: int = 60):
    try:
        # Create a BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        # Set the expiry time for the SAS
        expiry_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Generate the SAS token
        sas_token = generate_blob_sas(
            account_key=config.RERA_STORAGE_ACCOUNT_KEY,
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),  # Grant read permissions
            expiry=expiry_time
        )

        # Construct the SAS URL
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        return blob_url

    except Exception as e:
        return(f"Error generating SAS URL: {str(e)}")
        
