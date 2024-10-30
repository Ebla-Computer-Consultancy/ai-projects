from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from fastapi import APIRouter
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
from typing import List

router = APIRouter()

@router.post("/chat/{bot_name}")
async def chat(bot_name: str,message_payload: ChatPayload):
    return await chatbotservice.chat(bot_name,message_payload)
