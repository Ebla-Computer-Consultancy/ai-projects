from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from fastapi import APIRouter
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
from typing import List

router = APIRouter()

@router.post("/chat")
async def chat(message_payload: ChatPayload):
    return await chatbotservice.chat(message_payload)
