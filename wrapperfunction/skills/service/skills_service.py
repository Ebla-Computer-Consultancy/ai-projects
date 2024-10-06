from fastapi import HTTPException
from wrapperfunction.integration.skills_connector import read_scaned_pdf
import io

def extract_text(file_contents):
    try:
        print("================================================================")
        pdf_stream = io.BytesIO(file_contents)
        read_scaned_pdf(pdf_stream)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read new content file: {str(e)}")
    