
from fastapi import APIRouter
import wrapperfunction.text_analysis.service.text_analysis_service as text_analysis_service 
router = APIRouter()
@router.post("/semantic_analysis/")
def apply_analysis():
    return text_analysis_service.perform_semantic_analysis()
@router.post("/add_feedback/")
def add_feedback(conv_id: str, feedback: int):
    return text_analysis_service.perform_feedback_update(conv_id, feedback)


