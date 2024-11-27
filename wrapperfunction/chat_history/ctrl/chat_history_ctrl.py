from typing import Optional
from fastapi import APIRouter
import wrapperfunction.chat_history.service.chat_history_service as historyservice
from wrapperfunction.chatbot.model.chat_payload import ChatPayload


router = APIRouter()

@router.get("/conversations/")
def get_chats(user_id: str):
    return historyservice.get_conversations(user_id)
@router.get("/chat/")
def get_chats(conv_id: str):
    return historyservice.get_messages(conv_id)


@router.get("/all-conversations/")
def get_chats(bot_name:Optional[str]=None):
    return historyservice.get_all_conversations(bot_name)

@router.post("/sentiment-analysis/")
def apply_analysis():
    return historyservice.perform_sentiment_analysis()
@router.post("/add-feedback/")
def add_feedback(conv_id: str, feedback: int):
    return historyservice.perform_feedback_update(conv_id, feedback)
@router.get("/bot-names/")
def get_bot_name():
    return historyservice.get_bot_name()

@router.post("/add-message/")
async def add_message(chat_payload:ChatPayload,bot_name:str):
    return await historyservice.add_message(chat_payload,bot_name)