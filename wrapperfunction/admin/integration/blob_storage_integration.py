from wrapperfunction.core import config
from azure.storage.blob import BlobServiceClient

connect_str = config.STORAGE_CONNECTION
container_name = config.BLOB_CONTAINER_NAME


def get_blob_client(blob_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    return blob_service_client.get_blob_client(container=container_name, blob=blob_name)
