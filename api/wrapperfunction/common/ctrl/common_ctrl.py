
from fastapi import APIRouter, UploadFile
import wrapperfunction.common.service.common_service as commonservice

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile):
    return await commonservice.transcribe(file)
