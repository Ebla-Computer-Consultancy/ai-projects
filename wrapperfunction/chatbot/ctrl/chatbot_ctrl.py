from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from fastapi import APIRouter,UploadFile
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
from typing import List, Optional

router = APIRouter()


@router.post("/chat/{bot_name}")
async def chat(bot_name: str,message_payload: ChatPayload):
    return await chatbotservice.chat(bot_name,message_payload)
@router.post("/upload_documents/")
async def upload(files:List[UploadFile],bot_name,conversation_id: Optional[str] = None):
    return await chatbotservice.upload_documents(files,bot_name,conversation_id)
