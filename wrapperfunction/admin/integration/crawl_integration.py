from urllib import request
from urllib.parse import urljoin, urlparse
import uuid
import os
import json
from scrapy.crawler import CrawlerProcess
from azure.storage.blob import BlobServiceClient, BlobBlock
from wrapperfunction.admin.integration.storage_connector import upload_file_to_azure
from wrapperfunction.core.utls.spiders.crawling_spider import CrawlingSpider
from wrapperfunction.core.utls.helper import process_text_name
import wrapperfunction.core.config as config
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from bs4 import BeautifulSoup
import requests

AZURE_STORAGE_CONNECTION_STRING = config.RERA_STORAGE_CONNECTION
CONTAINER_NAME = config.RERA_CONTAINER_NAME
SUBFOLDER_NAME = config.RERA_SUBFOLDER_NAME
DOCS_SUBFOLDER_NAME = config.RERA_DOCS_SUBFOLDER_NAME

# Azure AI Document Intelligence configuration
AI_DI_endpoint = "https://rera-alaa-di.cognitiveservices.azure.com/t"
AI_DI_api_key = "55941486c1f643c083855fc2cf770e3d"
# document_analysis_client = DocumentAnalysisClient(AI_DI_endpoint, AzureKeyCredential(AI_DI_api_key))

def run_crawler(link: str):
    # Generate a unique filename
    # print("----------------1------------------")
    filename = f'export_{uuid.uuid4()}.json'
    filepath = f'./{filename}'

    # Run Scrapy spider
    process = CrawlerProcess({
        'FEED_URI': f'file:{filepath}',
        'FEED_FORMAT': 'json',
        'FEED_EXPORT_ENCODING': 'utf-8',
    })
    process.crawl(CrawlingSpider, start_urls=[link])
    process.start()

    return filepath , filename

def process_and_upload(filepath: str, link: str):
    # Process the JSON data
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    with open(filepath, 'r', encoding='utf-8') as file:
        # Load the JSON data
        data = json.load(file)
        # Split the JSON lines into individual files

        folder_path = "./export/" + filepath[2:-5]
        os.makedirs(folder_path, exist_ok=True)
        process_json_data_and_upload(data, blob_service_client, folder_path, link)
    os.remove(filepath)

def process_json_data_and_upload(data, blob_service_client,folder_path,link):
    for i, item in enumerate(data):
        # Generate a unique filename for each JSON object
        individual_filename = process_text_name(item["url"])
        if i == 0:
             str_ = individual_filename[:5]
        if str_ in individual_filename[:10]:
            individual_filename = f'item_{individual_filename}.json'
            individual_filepath = f'{folder_path}/{individual_filename}'
            print(individual_filepath)
            with open(individual_filepath, 'w', encoding="utf-8") as file:
                     json.dump(item, file, ensure_ascii=False)

            # Upload the file to Azure Blob Storage
        
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=f'{SUBFOLDER_NAME}/{individual_filename}')
        
            with open(individual_filepath, 'r', encoding="utf-8") as data:
                # Read the file content
                file_content = data.read()
                # Convert the content to bytes
                file_bytes = file_content.encode('utf-8')
                blob_client.upload_blob(file_bytes, overwrite=True)
                # Retrieve existing metadata, if desired
                blob_metadata = blob_client.get_blob_properties().metadata or {}
                more_blob_metadata = {'website_url': link[:-1], 'ref_url': item["url"]}
                blob_metadata.update(more_blob_metadata)
                # print(blob_metadata)

                # Set metadata on the blob
                blob_client.set_blob_metadata(metadata=blob_metadata)

            os.remove(individual_filepath)

def upload_files_to_blob(folder_path, subfolder_name=DOCS_SUBFOLDER_NAME, container_name=CONTAINER_NAME, connection_string=AZURE_STORAGE_CONNECTION_STRING):
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
                blob_path = f'{subfolder_name}/{file_name}'
            
                # Get the blob client
                blob_client = container_client.get_blob_client(blob=blob_path)
                # Open the file in binary mode
                with open(file_path, 'rb') as data:
                    file_size = os.path.getsize(file_path)
                    chunk_size = 4 * 1024 * 1024  # 4MB
                    blocks = []
                    block_id = 0
                
                    while True:
                        chunk = data.read(chunk_size)
                        if not chunk:
                            break
                        block_id_str = f'{block_id:06d}'
                        blob_client.stage_block(block_id_str, chunk)
                        blocks.append(BlobBlock(block_id=block_id_str))
                        block_id += 1
                
                blob_client.commit_block_list(blocks)

def delete_blobs_base_on_metadata(metadata_key,metadata_value,subfolder_name = SUBFOLDER_NAME,container_name=CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)

    blobs = container_client.list_blobs(name_starts_with=f"{subfolder_name}/")
    
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        blob_metadata = blob_client.get_blob_properties().metadata             
        if blob_metadata.get(metadata_key) == metadata_value:
            blob_client.delete_blob()

def delete_base_on_subfolder(subfolder_name = SUBFOLDER_NAME,container_name=CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)   
    blobs = container_client.list_blobs(name_starts_with=subfolder_name)

    for blob in blobs:
        print(f"Blob: {blob.name}")
        blob_client = container_client.get_blob_client(blob)
        blob_client.delete_blob()

def edit_blob_by_new_jsonfile(metadata_key,metadata_value,new_content, subfolder_name = SUBFOLDER_NAME,container_name=CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs(name_starts_with=f"{subfolder_name}/")
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

            return JSONResponse(content={"message": f"Blob with metadata {metadata_key}={metadata_value} edited successfully"}, status_code=200)
    return HTTPException(status_code=404, detail="Blob not found")    



def process_pdf(blob_name,container_name=CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    # Download PDF from Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    print("------------------------start---------------------------")
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    download_stream = blob_client.download_blob()
    pdf_content = download_stream.readall()

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

        # Extract the list of web URLs and target classes
        web_urls = config.ENTITY_MEDIA_SETTINGS.get("web_urls", [])
        target_classes = config.ENTITY_MEDIA_SETTINGS.get("a_class", [])
        
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
        # Extract target classes for p and img
        target_p_classes = config.ENTITY_MEDIA_SETTINGS.get("p_class", [])
        target_img_classes = config.ENTITY_MEDIA_SETTINGS.get("img_class", [])

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
