from wrapperfunction.chat_history.service.chat_history_service import upload_documents
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from fastapi import APIRouter,Request,UploadFile
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
from typing import List, Optional

router = APIRouter()

@router.post("/chat/{bot_name}")
async def chat(request: Request,bot_name: str,message_payload: ChatPayload):
    return await chatbotservice.chat(bot_name,message_payload,request)

@router.post("/upload_documents/")
async def upload(files:List[UploadFile],request: Request,bot_name,conversation_id: Optional[str] = None):
    return await upload_documents(files,bot_name,request,conversation_id)
