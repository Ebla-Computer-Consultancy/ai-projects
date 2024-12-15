from fastapi import UploadFile
from wrapperfunction.document_intelligence.integration.document_intelligence_connector import (
    analyze_file,
)

def inline_read_scanned_pdf(file: UploadFile | None, file_bytes: bytes = None):
    if file or file_bytes:
        result = analyze_file(file, "prebuilt-read", file_bytes)

        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
        return extracted_text
