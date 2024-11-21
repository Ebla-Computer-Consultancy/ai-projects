import os
import json
from fastapi import HTTPException
from scrapy.crawler import CrawlerProcess
from azure.storage.blob import BlobServiceClient, BlobBlock
from wrapperfunction.core.utls.spiders.crawling_spider import (
    CrawlingSpider,
)
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from wrapperfunction.admin.integration.skills_connector import inline_read_scanned_pdf
import wrapperfunction.core.config as config
from fastapi.responses import JSONResponse

AZURE_STORAGE_CONNECTION_STRING = config.STORAGE_CONNECTION
BLOB_CONTAINER_NAME = config.BLOB_CONTAINER_NAME
SUBFOLDER_NAME = config.SUBFOLDER_NAME


def run_crawler(
    urls: str,
    headers: dict = None,
    cookies: dict = None,
    deepCrawling: bool = False,
):
    process = CrawlerProcess()
    if deepCrawling:
        CrawlingSpider.rules = (
            Rule(
                LinkExtractor(),
                callback="parse_items",
                follow=True,
            ),
        )
    else:
        CrawlingSpider.rules = (
            Rule(
                callback="parse_items",
                follow=False,
            ),
        )
    process.crawl(CrawlingSpider, start_urls=urls, cookies=cookies, headers=headers)
    process.start()


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


def upload_files_to_blob(
    folder_path,
    subfolder_name=SUBFOLDER_NAME,
    container_name=BLOB_CONTAINER_NAME,
    connection_string=AZURE_STORAGE_CONNECTION_STRING,
):
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    # Iterate over all files in the specified folder
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # Construct the full file path
            file_path = os.path.join(root, file_name)
            # Construct the blob path
            blob_path = f"{subfolder_name}/{file_name}"
            # Get the blob client
            blob_client = container_client.get_blob_client(blob=blob_path)
            # Open the file in binary mode
            with open(file_path, "rb") as data:
                file_size = os.path.getsize(file_path)
                chunk_size = 4 * 1024 * 1024  # 4MB
                blocks = []
                block_id = 0

                while True:
                    chunk = data.read(chunk_size)
                    if not chunk:
                        break
                    block_id_str = f"{block_id:06d}"
                    blob_client.stage_block(block_id_str, chunk)
                    blocks.append(BlobBlock(block_id=block_id_str))
                    block_id += 1

            blob_client.commit_block_list(blocks)


def delete_blobs_base_on_metadata(
    metadata_key,
    metadata_value,
    subfolder_name=SUBFOLDER_NAME,
    container_name=BLOB_CONTAINER_NAME,
    connection_string=AZURE_STORAGE_CONNECTION_STRING,
):
    delete_blob(metadata_key=metadata_key, metadata_value=metadata_value)


def delete_base_on_subfolder(
    subfolder_name=SUBFOLDER_NAME,
    container_name=BLOB_CONTAINER_NAME,
    connection_string=AZURE_STORAGE_CONNECTION_STRING,
):
    delete_blob(container_name=container_name, subfolder_name=subfolder_name)


def delete_blob(
    metadata_key=None,
    metadata_value=None,
    subfolder_name=SUBFOLDER_NAME,
    container_name=BLOB_CONTAINER_NAME,
    connection_string=AZURE_STORAGE_CONNECTION_STRING,
):
    container_client, blobs = blob_client(
        subfolder_name, container_name, connection_string
    )
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        blob_metadata = blob_client.get_blob_properties().metadata
        if metadata_key == None:
            if blob_metadata.get(metadata_key) == metadata_value:
                blob_client.delete_blob()
        else:
            blob_client.delete_blob()


def edit_blob_by_new_jsonfile(
    metadata_key,
    metadata_value,
    new_content,
    subfolder_name=SUBFOLDER_NAME,
    container_name=BLOB_CONTAINER_NAME,
    connection_string=AZURE_STORAGE_CONNECTION_STRING,
):
    container_client, blobs = blob_client(
        subfolder_name, container_name, connection_string
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


def blob_client(
    subfolder_name=SUBFOLDER_NAME,
    container_name=BLOB_CONTAINER_NAME,
    connection_string=AZURE_STORAGE_CONNECTION_STRING,
):
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs(name_starts_with=f"{subfolder_name}/")
    return container_client, blobs
