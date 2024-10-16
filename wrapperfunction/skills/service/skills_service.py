from io import BytesIO
from fastapi import HTTPException
from wrapperfunction.integration.skills_connector import read_scanned_pdf


def extract_text(pdf_bytes: BytesIO):
    try:
        return read_scanned_pdf(pdf_bytes)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read new content file: {str(e)}"
        )
