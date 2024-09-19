import uuid
import os
import json
from scrapy.crawler import CrawlerProcess
from azure.storage.blob import BlobServiceClient, BlobBlock, BlobPrefix
from wrapperfunction.admin.utls.spiders.crawling_spider import CrawlingSpider
from wrapperfunction.admin.utls.helper import process_text_name
import wrapperfunction.core.config as config
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

AZURE_STORAGE_CONNECTION_STRING = config.RERA_STORAGE_CONNECTION
CONTAINER_NAME = config.RERA_CONTAINER_NAME
SUBFOLDER_NAME = config.RERA_SUBFOLDER_NAME
DOCS_SUBFOLDER_NAME = config.RERA_DOCS_SUBFOLDER_NAME

# Azure AI Document Intelligence configuration
AI_DI_endpoint = "https://rera-alaa-di.cognitiveservices.azure.com/t"
AI_DI_api_key = "55941486c1f643c083855fc2cf770e3d"
document_analysis_client = DocumentAnalysisClient(AI_DI_endpoint, AzureKeyCredential(AI_DI_api_key))

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
    poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_content)
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