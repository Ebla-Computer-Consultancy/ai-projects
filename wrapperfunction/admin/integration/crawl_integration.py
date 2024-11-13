import uuid
import os
import re
import json
from scrapy.crawler import CrawlerProcess
from azure.storage.blob import BlobServiceClient, BlobBlock, BlobPrefix
from wrapperfunction.core.utls.spiders.crawling_spider import CrawlingSpider, CrawlingPagesSpider
from wrapperfunction.admin.integration.skills_connector import inline_read_scanned_pdf
from wrapperfunction.core.utls.helper import process_text_name
import wrapperfunction.core.config as config
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from azure.core.credentials import AzureKeyCredential
import urllib.parse
import pandas as pd
# from azure.ai.formrecognizer import DocumentAnalysisClient

AZURE_STORAGE_CONNECTION_STRING = config.RERA_STORAGE_CONNECTION
BLOB_CONTAINER_NAME = config.RERA_CONTAINER_NAME
SUBFOLDER_NAME = config.RERA_SUBFOLDER_NAME


def run_crawler(link: str):
    # Generate a unique filename
    filename = f'export_{uuid.uuid4()}.json'
    filepath = f'./{filename}'
    #filepath2 = f'./export/docs/{filename}'


    # Run Scrapy spider
    process = CrawlerProcess({
         'FEED_URI': f'file:{filepath}',
         'FEED_FORMAT': 'json',
         'FEED_EXPORT_ENCODING': 'utf-8',
    })
    process.crawl(CrawlingSpider, start_urls=[link])
    process.start()

    return filepath, filename



def scrape_csv(csv_file_path,container_name):
    df = pd.read_csv(csv_file_path)
    urls = df['URL'].tolist()
    
    # Run the Scrapy spider
    process = CrawlerProcess({
         'FEED_URI': f'file:./{container_name}.json',
         'FEED_FORMAT': 'json',
         'FEED_EXPORT_ENCODING': 'utf-8',
    })
    process.crawl(CrawlingPagesSpider,start_urls=urls)
    process.start()


def process_and_upload(filepath: str,exportpath:str, link: str, doc =False, container_name = BLOB_CONTAINER_NAME):
    # Process the JSON data
    with open(filepath, "r", encoding="utf-8") as file:

        # Load the JSON data
        data = json.load(file)
        data = filter_social_media_urls(data)
        # Split the JSON lines into individual files
        # print("docccccccccccccccccccccc1",doc)
        if doc:
            folder_path = exportpath + filepath[2:-5] +"/transcription/"
        else:
            folder_path = exportpath + filepath[2:-5]
        os.makedirs(folder_path, exist_ok=True)
        for i, item in enumerate(data):

            individual_filepath, individual_filename= filter_json2file(item, folder_path)
            if doc:
                push_blob(individual_filepath,individual_filename, metadata_1 = link[:-1], metadata_2= item["url"], metadata_3= "crawled", metadata_4= "pdf",SUBFOLDER_NAME =SUBFOLDER_NAME,container_name=container_name)# 
                
            else:
                push_blob(individual_filepath,individual_filename, metadata_1 = link[:-1],metadata_2= item["url"], metadata_3= "crawled", metadata_4= "link",SUBFOLDER_NAME =SUBFOLDER_NAME,container_name=container_name)

def split_json_file(input_file, non_pdf_output_file, pdf_output_file):
    with open(input_file, 'r', encoding='utf8') as file:
        data = json.load(file)

    non_pdf_data = []
    pdf_data = []

    for item in data:
        if 'pdf_url' in item:
            pdf_data.append(item)
        else:
            non_pdf_data.append(item)

    with open(non_pdf_output_file, 'w', encoding='utf8') as file:
        json.dump(non_pdf_data, file, ensure_ascii=False, indent=4)

    with open(pdf_output_file, 'w', encoding='utf8') as file:
        json.dump(pdf_data, file, ensure_ascii=False, indent=4)

def sanitize_filename(filename):
    return re.sub(r'[<>:"\\|?*]', '', filename)

def update_json_with_pdf_text(json_file, folder_path):
    with open(json_file, 'r', encoding='utf8') as file:
        data = json.load(file)
    for item in data:
        if 'pdf_url' in item:
            item['url'] = item.pop('pdf_url')
            pdf_filename = item['title']
            pdf_path = folder_path+"/"+pdf_filename
            # Extract text from the PDF
            extracted_text = inline_read_scanned_pdf(pdf_path)
            # Append the extracted text to the JSON item
            item['body'] = extracted_text
    
    # Save the updated JSON back to the file
    with open('updated_' + json_file[2:], 'w', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def filter_social_media_urls(data):
    social_media_domains = ["instagram.com", "x.com", "facebook.com", "youtube.com","play.google.com","apps.apple.com","careers.phcc.gov.qa"]
    filtered_data = [entry for entry in data if not any(domain in entry['url'] for domain in social_media_domains)]
    return filtered_data

def filter_json2file(item, folder_path, return_flag= True):
    individual_filename = process_text_name(item["url"])
    individual_filename = f'item_{individual_filename}.json'
    individual_filepath = f'{folder_path}/{individual_filename}'
    with open(individual_filepath, 'w', encoding="utf-8") as file:
        json.dump(item, file, ensure_ascii=False)
    if return_flag:
        return individual_filepath, individual_filename

def push_blob(individual_filepath,individual_filename,metadata_1 = None,metadata_2= None, metadata_3= "crawled", metadata_4= None,container_name = BLOB_CONTAINER_NAME,SUBFOLDER_NAME=SUBFOLDER_NAME):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob= f'{SUBFOLDER_NAME}/{individual_filename}')
    encode = "utf-8"
    with open(individual_filepath, 'r', encoding=encode) as data:
        # Read the file content
        file_content = data.read()
        # Convert the content to bytes
        file_bytes = file_content.encode(encode)
        blob_client.upload_blob(file_bytes, overwrite=True)
        # Retrieve existing metadata, if desired
        encoded_url = urllib.parse.quote(metadata_2)
        if metadata_4 == "link":
            encoded_url = urllib.parse.unquote(encoded_url)
        if metadata_1 is not None and metadata_2 is not None:
            blob_metadata = blob_client.get_blob_properties().metadata or {}
            more_blob_metadata = {'website_url': metadata_1,'ref_url': encoded_url, 'indexing_type': metadata_3, 'type': metadata_4}
            blob_metadata.update(more_blob_metadata)
        # print(blob_metadata)

        # Set metadata on the blob
        blob_client.set_blob_metadata(metadata=blob_metadata)

        # os.remove(individual_filepath)


def upload_files_to_blob(folder_path, subfolder_name=SUBFOLDER_NAME, container_name=BLOB_CONTAINER_NAME, connection_string=AZURE_STORAGE_CONNECTION_STRING):
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

def delete_blobs_base_on_metadata(metadata_key,metadata_value,subfolder_name = SUBFOLDER_NAME,container_name=BLOB_CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    delete_blob(metadata_key = metadata_key,metadata_value = metadata_value)

def delete_base_on_subfolder(subfolder_name = SUBFOLDER_NAME,container_name=BLOB_CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    delete_blob(container_name=container_name,subfolder_name = subfolder_name)

def delete_blob(metadata_key = None,metadata_value = None,subfolder_name = SUBFOLDER_NAME,container_name=BLOB_CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    print("alaaa0")
    container_client, blobs= blob_client(subfolder_name,container_name,connection_string)
    print("alaaa1")
    for blob in blobs:
        print("alaaa")
        blob_client = container_client.get_blob_client(blob)
        blob_metadata = blob_client.get_blob_properties().metadata             
        if metadata_key == None:
             if blob_metadata.get(metadata_key) == metadata_value:
                  blob_client.delete_blob()
        else:
            blob_client.delete_blob()

def edit_blob_by_new_jsonfile(metadata_key,metadata_value,new_content, subfolder_name = SUBFOLDER_NAME,container_name=BLOB_CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    container_client, blobs= blob_client(subfolder_name,container_name,connection_string)

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

def blob_client(subfolder_name = SUBFOLDER_NAME,container_name=BLOB_CONTAINER_NAME,connection_string =AZURE_STORAGE_CONNECTION_STRING):
    print("====================")
    print(connection_string)
    print(container_name)
    print(subfolder_name)
    print("====================")
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    print("-----1----")
    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    print("-----2----")
    blobs = container_client.list_blobs(name_starts_with=f"{subfolder_name}/")
    print("-----3----")
    return container_client, blobs

