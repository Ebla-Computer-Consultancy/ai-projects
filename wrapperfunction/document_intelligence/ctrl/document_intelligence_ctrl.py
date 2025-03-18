
from typing import Optional
from fastapi import APIRouter, File, UploadFile
import wrapperfunction.document_intelligence.service.document_intelligence_service as documentintelligenceservice
from fastapi import  UploadFile



router = APIRouter()



@router.post("/analyze-pdf")
def document_intelligence(model_id: str = "prebuilt-layout", file: UploadFile = File()):
    return documentintelligenceservice.analyze_file(
        model_id, "document_intelligence_chatbot", file
    )


@router.post("/auto-split-pdf/")
async def upload_file(file: UploadFile ,bot_name,criteria:Optional[str] = None):
    try:
        return documentintelligenceservice.auto_split_pdf(file, criteria,bot_name)
    except Exception as e:
        return {"status": "error", "message": str(e)}