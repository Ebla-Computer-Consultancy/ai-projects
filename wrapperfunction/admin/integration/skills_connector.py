import base64
import os
from io import BytesIO
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import wrapperfunction.core.config as config

DI_ENDPOINT = config.DOCUMENT_INTELLIGENCE_ENDPOINT
DI_API_KEY = config.DOCUMENT_INTELLIGENCE_API_KEY
document_analysis_client = DocumentAnalysisClient(
    endpoint=DI_ENDPOINT, credential=AzureKeyCredential(DI_API_KEY)
)


def read_scanned_pdf(pdf_bytes: BytesIO):
    with open(pdf_bytes, "rb") as f:
         poller = document_analysis_client.begin_analyze_document(
            "prebuilt-read", document=f)
    result =  poller.result()
    extracted_text = ""
    for page in result.pages:
        for line in page.lines:
            print(line.content)
            extracted_text += line.content + "\n"
    return {"text": extracted_text}

def read_scanned_pdf_skill(request):
    responses = []
    value = request.values[0]
    try:
        pdf_bytes = BytesIO(base64.b64decode(value.data["data"]))
        poller = document_analysis_client.begin_analyze_document("prebuilt-read", document=pdf_bytes)
        result = poller.result()
        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
        response = {
                "recordId": value.recordId,
                "data": {"text": extracted_text}
            }
        responses.append(response)
        print(responses)
    except Exception as e:
        error_response = {
                "recordId": value.recordId,
                "errors": [{"message": str(e)}]
            }
        responses.append(error_response)
    return {"values": responses}



def inline_read_scanned_pdf(pdf_path):
        print("pdf_path",pdf_path)
        if pdf_path.endswith(".pdf"):
            with open(pdf_path, "rb") as f:
                poller = document_analysis_client.begin_analyze_document("prebuilt-read", document=f)
                result = poller.result()
                
                extracted_text = ""
                for page in result.pages:
                    for line in page.lines:
                        extracted_text += line.content + "\n"
                # print(extracted_text)
                return extracted_text

"""
from azure.storage.blob import BlobServiceClient
container_name = "test1"
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
                output_file_path = os.path.join("C:/Users/alaa/Desktop/SHAI Club/github/ai-projects/export/temp", filename)
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(extracted_text)
                
                print(f"Uploaded OCR results for {filename} to Azure Storage.")

# Example usage
folder_path = "C:/Users/alaa/Desktop/EBLA/dsfsdfsdef/export/docs/export_b10eb000-aab0-4bea-9ba2-b02a7cdde886"
read_and_upload_pdfs(folder_path)
"""
