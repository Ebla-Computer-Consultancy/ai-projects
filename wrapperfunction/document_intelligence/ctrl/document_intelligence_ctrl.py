from fastapi import APIRouter, File, UploadFile
import wrapperfunction.document_intelligence.service.document_intelligence_service as documentintelligenceservice

router = APIRouter()


@router.post("/document-intelligence")
def document_intelligence(model_id: str = "prebuilt-layout", file: UploadFile = File()):
    return documentintelligenceservice.analyze_file(
        model_id, "document_intelligence_chatbot", file
    )
