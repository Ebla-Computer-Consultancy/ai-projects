from io import BytesIO
from turtle import pd
import uuid
import os
import re
import json
from fastapi import HTTPException
from scrapy.crawler import CrawlerProcess
from wrapperfunction.admin.integration.skills_connector import inline_read_scanned_pdf
import wrapperfunction.core.config as config
from fastapi.responses import JSONResponse
from fastapi import HTTPException, UploadFile
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

from wrapperfunction.core.utls.spiders.crawling_spider import CrawlingPagesSpider, CrawlingSpider

AZURE_STORAGE_CONNECTION_STRING = config.RERA_STORAGE_CONNECTION
BLOB_CONTAINER_NAME = config.RERA_CONTAINER_NAME
SUBFOLDER_NAME = config.RERA_SUBFOLDER_NAME


def run_crawler(urls: str, deepCrawling: bool = False):
    process = CrawlerProcess()
    if deepCrawling:
        CrawlingSpider.rules = (
            Rule(
                LinkExtractor(
                    deny=(
                        "instagram.com",
                        "x.com",
                        "facebook.com",
                        "youtube.com",
                        "play.google.com",
                        "apps.apple.com",
                        "careers.phcc.gov.qa",
                    )
                ),
                callback="parse_items",
                follow=True,
            ),
        )
    else:
        CrawlingSpider.rules = (Rule(callback="parse_items"),)
    process.crawl(
        CrawlingSpider,
        start_urls=urls,
        # cookies={"LangSwitcher_Setting": "ar-SA"}, // cookies for khrama
    )
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
    # Analyze PDF using Document Intelligence
    print("------------------------0---------------------------")
    # poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_content)
    poller = None
    print("------------------------0.1---------------------------")
    result = poller.result()
    print("------------------------0.2---------------------------")
    # Extract and process data
    extracted_data = {}
    for page in result.pages:
        for table in page.tables:
            for cell in table.cells:
                extracted_data[cell.content] = cell.bounding_box

    # Save processed data back to Blob Storage or another database
    print("------------------------1---------------------------")
    processed_blob_name = f"processed_{blob_name}.json"
    processed_blob_client = blob_service_client.get_blob_client(container=container_name, blob=processed_blob_name)
    print("------------------------2---------------------------")
    processed_blob_client.upload_blob(str(extracted_data), overwrite=True)
    print("------------------------3---------------------------")
    print(f"Processed data saved to {processed_blob_name}")


def transcript_pdfs(container_name=CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_list = blob_service_client.get_container_client(container_name).list_blobs()
    for blob in blob_list:
        if blob.name.endswith(".pdf"):
            process_pdf(blob.name)

def get_all_Links_in_urls(urls: list):
    try:
        media_settings = config.ENTITY_SETTINGS.get("media_settings",{})
        # Extract the list of web URLs and target classes
        web_urls = media_settings.get("web_urls", [])
        target_classes = media_settings.get("a_class", [])
        
        # Initialize a list to store the links
        news_links_list = []

        # Iterate over the provided URLs
        for url in urls:
            # If the URL is not in the list of web URLs in the config, skip it
            if url not in web_urls:
                print(f"URL {url} is not in the configured web URLs. Skipping.")
                continue

            # Fetch and parse the HTML content of the URL
            response = requests.get(url)
            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")

            # Initialize a list to store links for the current URL
            links = []

            # Search for <div> elements with the specified classes
            for div_class in target_classes:
                divs = soup.find_all("div", class_=div_class)

                # Within each <div>, find all <a> tags and retrieve their href attributes
                for div in divs:
                    for link in div.find_all("a", href=True):
                        href = link["href"]
                        if "#" not in href:
                            # If href is relative, convert it to an absolute URL
                            absolute_href = urljoin(url, href) if not href.startswith(url) else href
                            if absolute_href not in links:
                                links.append(absolute_href)                       

            # Add the URL and its links to the final JSON structure
            news_links_list.append({
                "url": url,
                "links": links
            })

        return news_links_list

    except Exception as e:
        return f"ERROR getting links: {str(e)}"

def save_media_with_topics(news_links: list, topics: list, container_name: str, connection_string: str):
    try:
        media_settings = config.ENTITY_SETTINGS.get("media_settings",{})
        # Extract target classes for p and img
        target_p_classes = media_settings.get("p_class", [])
        target_img_classes = media_settings.get("img_class", [])

        for entry in news_links:
            url = entry["url"]
            links = entry["links"]

            for link in links:
                print(f"\nProcessing Link from {url}: {link}\n\n")
                response = requests.get(link)
                html_content = response.content

                soup = BeautifulSoup(html_content, "html.parser")

                # Initialize sets to store unique texts and filtered image links
                relevant_texts = set()
                filtered_imgs_links = set()

                # Find div elements with specified p_class and extract unique paragraphs
                for p_class in target_p_classes:
                    for div in soup.find_all("div", class_=p_class):
                        for p_tag in div.find_all("p"):
                            paragraph_text = p_tag.get_text(strip=True)
                            if any(topic in paragraph_text for topic in topics):
                                relevant_texts.add(paragraph_text)

                # Find div elements with specified img_class and extract unique image URLs
                for img_class in target_img_classes:
                    for div in soup.find_all("div", class_=img_class):
                        for img_tag in div.find_all("img"):
                            img_url = img_tag.get("src")
                            print(f"url:{img_url}\n")
                            if img_url:
                                #TODO edit logo
                                if "logo" not in img_url and is_valid_url(img_url, url):
                                    if str(img_url).endswith(tuple([".png",".PNG",".JPG",".jpg",".jpeg",".JPEG"])): 
                                        # Convert to absolute URL if it's relative
                                        absolute_img_url = img_url if img_url.startswith('https') else urljoin(url, img_url)
                                        filtered_imgs_links.add(absolute_img_url)
                                else:
                                    print(f"NOT Valid IMG_URL:{img_url}")
                print(f"IMGS:\n{filtered_imgs_links}")
                if relevant_texts:
                    # Prepare JSON data to store in Azure Blob
                    content_data = {
                        "ref_url": url,
                        "url": link,
                        "content": "\n".join(relevant_texts),
                        "images_urls": list(filtered_imgs_links)
                    }

                    # Convert JSON data to string for upload
                    json_content = json.dumps(content_data, ensure_ascii=False)
                    
                    # Create the JSON filename
                    link_filename = f"{link.replace('https://', '').replace('/', '_')}"
                    folder_name = f"{url.replace('https://', '').replace('/', '_')}"
                    blob_name = f"{folder_name}/{link_filename}.json"
                    
                    # Upload the JSON to Azure Blob Storage
                    upload_file_to_azure(json_content, container_name, blob_name, connection_string)

    except Exception as e:
        print(f"ERROR Saving Results: {str(e)}")
        
def is_valid_url(img_url, base_url):
    try:
        # Combine with base URL if img_url is relative
        absolute_url = urljoin(base_url, img_url)
        if img_url.startswith(('http', 'https')):
            absolute_url = img_url

        # Parse and validate URL format
        parsed_url = urlparse(absolute_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False

        # Send a HEAD request to check if the URL is reachable
        response = requests.head(absolute_url, allow_redirects=True)
        if response.status_code == 200:
            return True
        return False

    except Exception as e:
        print(f"Error checking URL {img_url}: {e}")
        return False
