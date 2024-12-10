from wrapperfunction.core import config
from azure.storage.blob import BlobServiceClient

connect_str = config.STORAGE_CONNECTION


def get_blob_client(container_name:str, blob_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    return blob_service_client.get_blob_client(container=container_name, blob=blob_name)

def get_container_client(
    container_name:str,
    subfolder_name:str
    
):
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    if subfolder_name is not None:
        blobs = container_client.list_blobs(name_starts_with=f"{subfolder_name}/")
    else:
        blobs = container_client.list_blobs()
    return container_client, blobs