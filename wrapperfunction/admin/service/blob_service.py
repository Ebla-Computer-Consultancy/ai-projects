from wrapperfunction.admin.integration.blob_storage_integration import get_blob_client
from azure.storage.blob import BlobType
import urllib.parse

from wrapperfunction.core import config


def append_blob(
    blob_name: str,
    blob: str,
    folder_name: str = config.SUBFOLDER_NAME,
    metadata_1=None,
    metadata_2=None,
    metadata_3="crawled",
    metadata_4=None,
):
    blob_client = get_blob_client(blob_name=f"{folder_name}/{blob_name}")
    blob_client.upload_blob(blob, blob_type=BlobType.AppendBlob, overwrite=True)

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
