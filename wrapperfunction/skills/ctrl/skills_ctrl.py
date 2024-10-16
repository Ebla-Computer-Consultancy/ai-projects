from io import BytesIO
from fastapi import APIRouter, HTTPException
import wrapperfunction.skills.service.skills_service as skillsservice
from fastapi import HTTPException, UploadFile, File

router = APIRouter()


@router.post("/extract-text/")
async def extract_text(file: UploadFile = File()):
    try:
        pdf_bytesIO = BytesIO(file.file.read())
        return skillsservice.extract_text(pdf_bytesIO)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
