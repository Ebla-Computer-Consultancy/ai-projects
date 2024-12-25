import datetime
from wrapperfunction.core import config
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

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


def generate_blob_sas_url(container_name: str, blob_name: str, expiration_minutes: int = 60):
    try:
        blob_service_client = get_blob_client(container_name, blob_name)
        expiry_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)).strftime('%Y-%m-%dT%H:%M:%SZ')

        sas_token = generate_blob_sas(
            account_key=config.STORAGE_ACCOUNT_KEY,
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time
        )

        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        return blob_url

    except Exception as e:
        return(f"Error generating SAS URL: {str(e)}")
    