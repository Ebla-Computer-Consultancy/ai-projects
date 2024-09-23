from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
import wrapperfunction.core.config as config


AZURE_STORAGE_CONNECTION_STRING = config.RERA_STORAGE_CONNECTION
CONTAINER_NAME = config.RERA_CONTAINER_NAME
# SUBFOLDER_NAME = config.RERA_SUBFOLDER_NAME
# DOCS_SUBFOLDER_NAME = config.RERA_DOCS_SUBFOLDER_NAME


# Azure Blob Storage configuration
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_name = CONTAINER_NAME

# Azure AI Document Intelligence configuration
AI_DI_endpoint = "https://rera-alaa-di.cognitiveservices.azure.com/t"
AI_DI_api_key = "55941486c1f643c083855fc2cf770e3d"
document_analysis_client = DocumentAnalysisClient(AI_DI_endpoint, AzureKeyCredential(AI_DI_api_key))

def process_pdf(blob_name):
    # Download PDF from Blob Storage
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

# List and process all PDFs in the container
blob_list = blob_service_client.get_container_client(container_name).list_blobs()
for blob in blob_list:
    if blob.name.endswith(".pdf"):
        process_pdf(blob.name)
