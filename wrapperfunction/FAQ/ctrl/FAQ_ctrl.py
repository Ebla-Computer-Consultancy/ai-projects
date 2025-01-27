from typing import Optional
from fastapi import APIRouter
from wrapperfunction.FAQ.model.question_model import Question
from wrapperfunction.FAQ.service import FAQ_service 


router = APIRouter()
@router.post("/qustions/")
async def add_questions(questions: list[Question]):
    return await FAQ_service.add_questions(questions)

@router.delete("/questions/")
def delete_questions(rawkey: str):
    return  FAQ_service.delete_questions(rawkey)

@router.patch("/questions/")
def update_questions(rawkey: str,updated_data: Question):
    return  FAQ_service.update_question(rawkey,updated_data)
@router.get("/questions/")
def get_questions(bot_name: Optional[str] = None):
    return FAQ_service.get_questions(bot_name)