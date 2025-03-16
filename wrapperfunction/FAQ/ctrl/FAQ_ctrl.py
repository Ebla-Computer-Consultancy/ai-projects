from typing import Dict, List, Optional
from fastapi import APIRouter
from wrapperfunction.FAQ.model.question_model import Question
from wrapperfunction.FAQ.service import FAQ_service 


router = APIRouter()

@router.get("/faqs/")
def get_all_faqs():
    return FAQ_service.get_all_faqs()

@router.get("/faqs/archive/")
def get_archived_faqs(bot_name: str, limit: Optional[int] = None):
    return FAQ_service.get_archived_faqs(bot_name, limit)

@router.post("/faqs/archive/")
async def add_faq_to_archive(faqs_data: List[Dict]):
    return await FAQ_service.add_faqs_to_archive(faqs_data)

@router.put("/faqs/archive/")
def update_archived_faq(row_key: str, updated_data: Question):
    return FAQ_service.update_archived_faq(row_key, updated_data)

@router.delete("/faqs/archive/")
def delete_archived_faq(faqs_data: List[Dict]):
    return FAQ_service.delete_archived_faqs(faqs_data)
