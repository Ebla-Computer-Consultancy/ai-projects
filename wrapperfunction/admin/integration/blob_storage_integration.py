import datetime
from azure.storage.blob._models import BlobSasPermissions
from azure.storage.blob._shared_access_signature import generate_blob_sas
import urllib
from wrapperfunction.core import config
from azure.storage.blob import BlobServiceClient

connect_str = config.STORAGE_CONNECTION


def get_blob_service_client():
    return BlobServiceClient.from_connection_string(connect_str)

def get_blob_client(container_name:str, blob_name: str):
    blob_service_client = get_blob_service_client()
    return blob_service_client.get_blob_client(container=container_name, blob=blob_name)

def get_container_client(
    container_name:str,
    subfolder_name:str=None
    
):
    # Create the BlobServiceClient object
    blob_service_client = get_blob_service_client()
    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    if subfolder_name is not None:
        blobs = container_client.list_blobs(name_starts_with=f"{subfolder_name}/")
    else:
        blobs = container_client.list_blobs()
    return container_client, blobs

def generate_sas_token(blob_url: str = None, container_name: str = None, blob_name: str = None,account_name: str = None):
    try:
        if blob_url:
            parsed_url = urllib.parse.urlparse(blob_url)
            account_name = parsed_url.netloc.split('.')[0]
            path_parts = parsed_url.path.lstrip('/').split('/', 1)
            container_name = path_parts[0]
            blob_name = urllib.parse.unquote(path_parts[1])
        expiry_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%SZ')
        sas_token = generate_blob_sas(
            account_name=account_name,
            account_key=config.STORAGE_ACCOUNT_KEY,
            container_name=container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time
        )
        return sas_token

    except Exception as e:
        return f"Error generating SAS URL: {str(e)}"