
import os 
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import wrapperfunction.core.config as config

DI_ENDPOINT = config.DOCUMENT_INTELLIGENCE_ENDPOINT
DI_API_KEY = config.DOCUMENT_INTELLIGENCE_API_KEY
document_analysis_client = DocumentAnalysisClient(endpoint=DI_ENDPOINT, credential=AzureKeyCredential(DI_API_KEY))

def read_scaned_pdf(contents):
    print("----------1---------")
    # print(contents)
    # client = DocumentIntelligenceClient(DI_endpoint, AzureKeyCredential(DI_api_key))
    
    
    print("----------2---------")
    path = "C:/Users/alaa/Desktop/EBLA/pdfs/قانون-رقم-٢٩-بشأن-مراقبة-المباني.pdf"
    # path = contents
    # poller = document_analysis_client.begin_analyze_document(
    #         "prebuilt-read", document=contents)
    with open(path, "rb") as f:
         print(f)
         poller = document_analysis_client.begin_analyze_document(
            "prebuilt-read", document=f)
    print("----------3---------")
    result =  poller.result()
    print("----------4---------")
    extracted_text = ""
    for page in result.pages:
        for line in page.lines:
            print(line.content)
            extracted_text += line.content + "\n"
    print("----------5---------")
    print(extracted_text)
    return {"text": extracted_text}

"""
document_analysis_client = DocumentAnalysisClient(
    endpoint=DI_endpoint, credential=AzureKeyCredential(DI_api_key)
)
path = "C:/Users/alaa/Desktop/EBLA/pdfs/قانون-رقم-٢٩-بشأن-مراقبة-المباني.pdf"
with open(path, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-read", document=f
    )
result = poller.result()

for page in result.pages:
    for line in page.lines:
        print(line.content)
"""
# read_scaned_pdf(contents="alaa")

"""
from azure.storage.blob import BlobServiceClient
container_name = "rera-storage"
SUBFOLDER_NAME = "docs"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

document_analysis_client = DocumentAnalysisClient(endpoint=DI_endpoint, credential=AzureKeyCredential(DI_api_key))

def read_and_upload_pdfs(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "rb") as f:
                poller = document_analysis_client.begin_analyze_document("prebuilt-read", document=f)
                result = poller.result()
                
                extracted_text = ""
                for page in result.pages:
                    for line in page.lines:
                        extracted_text += line.content + "\n"
                
                # Upload the extracted text to Azure Blob Storage
                filename = filename.replace(".pdf", ".txt")
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=f'{SUBFOLDER_NAME}/{filename}')
                blob_client.upload_blob(extracted_text, overwrite=True)
                # Save the extracted text to a local file
                output_file_path = os.path.join("C:/Users/alaa/Desktop/SHAI Club/github/ai-projects/api/export/temp", filename)
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(extracted_text)
                
                print(f"Uploaded OCR results for {filename} to Azure Storage.")

# Example usage
folder_path = "C:/Users/alaa/Desktop/SHAI Club/github/ai-projects/api/export/docs/export_b10eb000-aab0-4bea-9ba2-b02a7cdde886"
read_and_upload_pdfs(folder_path)
"""