import base64
from io import BytesIO
from fastapi import UploadFile
from wrapperfunction.document_intelligence.integration.document_intelligence_connector import (
    analyze_file,
)


def read_scanned_pdf_skill(file: UploadFile, recordId):
    responses = []
    try:
        response = {
            "recordId": recordId,
            "data": {"text": inline_read_scanned_pdf(file)},
        }
        responses.append(response)
    except Exception as e:
        error_response = {"recordId": recordId, "errors": [{"message": str(e)}]}
        responses.append(error_response)
    return {"values": responses}


def inline_read_scanned_pdf(file: UploadFile):
    if file:
        result = analyze_file("prebuilt-read", document=file)

        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
        return extracted_text
