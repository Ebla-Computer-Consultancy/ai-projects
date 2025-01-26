from typing import Optional
from fastapi import APIRouter, Request
from wrapperfunction.chat_history.model.question_model import Question
import wrapperfunction.chat_history.service.chat_history_service as history_service
from wrapperfunction.chatbot.model.chat_payload import ChatPayload


router = APIRouter()

@router.get("/conversations/")
def get_conversations(user_id: str):
    return history_service.get_conversations(user_id)

@router.get("/chat/")
def get_chats(conv_id: str):
    return history_service.get_messages(conv_id)

@router.get("/all-conversations/")
def get_all_conversations(bot_name:Optional[str]=None):
    return history_service.get_all_conversations(bot_name)

@router.post("/sentiment-analysis/")
def apply_analysis():
    return history_service.perform_sentiment_analysis()

@router.post("/add-feedback/")
def add_feedback(conv_id: str, feedback: int):
    return history_service.perform_feedback_update(conv_id, feedback)

@router.get("/bot-names/")
def get_bot_name():
    return history_service.get_bot_name()

@router.post("/add-message/")
async def add_message(chat_payload:ChatPayload,bot_name:str,request: Request):
    return await history_service.add_message(chat_payload,bot_name,request)
  
@router.post("/qustions/")
async def add_questions(questions: list[Question]):
    return await history_service.add_questions(questions)

@router.delete("/questions/")
def delete_questions(rawkey: str):
    return  history_service.delete_questions(rawkey)

@router.patch("/questions/")
def update_questions(rawkey: str,updated_data: Question):
    return  history_service.update_question(rawkey,updated_data)
@router.get("/questions/")
def get_questions(bot_name: Optional[str] = None):
    return history_service.get_questions(bot_name)