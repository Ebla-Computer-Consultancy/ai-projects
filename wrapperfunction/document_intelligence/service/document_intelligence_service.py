
import ast
from io import BytesIO
import json
from typing import Dict, List, Optional, Tuple
import uuid
import zipfile
from fastapi import File, HTTPException, UploadFile
from pypdf import PdfReader, PdfWriter
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
import wrapperfunction.document_intelligence.integration.document_intelligence_connector as documentintelligenceconnector
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.admin.integration.storage_connector as storageconnector


def inline_read_scanned_pdf(file: UploadFile | None, file_bytes: bytes = None):
    if file or file_bytes:
        result = documentintelligenceconnector.analyze_file(file, "prebuilt-read", file_bytes)

        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
        return extracted_text

def analyze_file(model_id: str, bot_name: str, file: UploadFile = File()):
    try:
        poller_result = documentintelligenceconnector.analyze_file(file, model_id)
        file_result = {"content": poller_result.content, "tables": []}
        for index, table in enumerate(poller_result.tables):
            file_result["tables"].append({"cells": []})
            for cell in table["cells"]:
                file_result["tables"][index]["cells"].append(
                    {"content": cell["content"], "kind": cell.kind}
                )

        return chatbotservice.ask_open_ai_chatbot(
            bot_name=bot_name,
            chat_payload=ChatPayload(
                messages=[
                    {
                        "role": "user",
                        "content": json.dumps(
                            file_result,
                            ensure_ascii=False,
                        ),
                    }
                ]
            ),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        #   "content": "{'manufacturer':{'producer':'','supplier':'','company-name':'','manufacturer-supplier':'','manufacturers-name-and-Address':''},'trade-name':{'product-name':'','commercial-name':'','brand-name':'','product-identifier':'','proprietary-name':'','common-name':''},'chemical-name':{'substance-name':'','scientific-name':'','iupac-name':'','proper-Chemical-name':'','systematic-name':''},'cas-no':{'cas-registry-number':'','chemical-abstracts-service-number':'','cas-number':'','cas-identification-number':'','cas-rn':''},'state':{'physical-state':'','form':'','appearance':'','condition-Solid-Liquid-Gas':'','state-of-matter':''},'storage-condition':{'storage-requirements':'','storage-guidelines':'','storage-instructions':'','storage-information':'','storage-recommendations':''},'prevention-method':{'preventative-measures':'','safety-precautions':'','preventive-actions':'','hazard-prevention':'','precautionary-measures':''},'control-method':{'control-measures':'','exposure-controls':'','protection-measures':'','control-procedures':'','engineering-controls':''},'classification':{'hazard-classification':'','risk-classification':'','hazard-category':'','hazard-class':'','ghs-classification-globally-harmonized-system':''},'hs-code':{'harmonized-system-code':'','harmonized-tariff-code':'','hts-code':'','customs-code':'','tariff-code':''},'un-no':{'un-number':'','un-identification-number':'','united-nations-number':'','un-id':'','un-hazard-number':''}}"

def get_openai_instruction(prompt):

    try:
        response = openaiconnector.client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL,  
            messages=[{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with Azure OpenAI API: {e}"


def detection(text,criteria:Optional[str] = None):
    if not criteria:
        prompt = (
            "The following text is extracted from file. Identify the best practice to split this file. "
            "Return the results as a Python list of page number ranges without any extra text. Example: [[1, 10], [11, 20]].\n\n"
            f"{text}"
        )
    else:
        prompt = (
    f"The following text is extracted from a file. Split the file based on the following criteria: {criteria}. "
    "If splitting based on this criteria is not possible, identify the best practice for splitting the file. "
    "Return the results as a Python list of page number ranges (e.g., [[1, 10], [11, 20]])with no additional text. "
    "If no split is possible, return an empty list `[]` with no additional text.\n\n"
    f"{text}"
)
    try:
        content=get_openai_instruction(prompt)
        ranges = ast.literal_eval(content)
        if isinstance(ranges, list) and all(isinstance(r, list) and len(r) == 2 for r in ranges):
            return ranges
        else:
            raise ValueError("Invalid response format from OpenAI.")
    except Exception as e:
        return []




def extract_text_from_pdf(result) -> List[str]:
    return [
        "\n".join([line.content for line in page.lines])
        for page in result.pages
    ]

def get_page_ranges(full_text: str, criteria: str) -> List[List[int]]:
    ranges = detection(full_text, criteria)
    if not ranges or not isinstance(ranges, list):
        raise ValueError("Invalid or empty page ranges detected.")
    return ranges

def split_pdf(reader: PdfReader, ranges: List[List[int]]) -> List[Tuple[str, BytesIO]]:
    files = []
    for i, (start, end) in enumerate(ranges):
        writer = PdfWriter()
        for page_num in range(start - 1, end):
            if page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
        temp_file = BytesIO()
        writer.write(temp_file)
        temp_file.seek(0)
        files.append((f"split_{i + 1}.pdf", temp_file))
    return files

def create_zip(files: List[Tuple[str, BytesIO]]) -> BytesIO:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_name, file_content in files:
            zip_file.writestr(file_name, file_content.read())
    zip_buffer.seek(0)
    return zip_buffer

def upload_to_storage( zip_buffer: BytesIO) -> str:
    container_client=storageconnector.get_blob_service_client(config.SPLITER_CONTAINER_NAME)
    blob_name = f"{uuid.uuid4()}.zip"
    blob_response = container_client.upload_blob(name=blob_name, data=zip_buffer, overwrite=True)
    return blob_response.url

def auto_split_pdf(pdf: UploadFile, criteria: str) -> Dict:
    try:
        result =documentintelligenceconnector.analyze_file(pdf)
        text_per_page = extract_text_from_pdf(result)
        full_text = "\n".join(f"Page {i + 1}:\n{text}" for i, text in enumerate(text_per_page))
        page_ranges = get_page_ranges(full_text, criteria)
        page_ranges.append([len(result.pages) + 1])
        reader = PdfReader(pdf.file)
        split_files = split_pdf(reader, page_ranges[:-1])
        zip_buffer = create_zip(split_files)
        zip_url = upload_to_storage(zip_buffer)
        return {
            "status": "success",
            "message": "Zip file uploaded successfully",
            "url": zip_url,
            "ranges": page_ranges[:-1],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}