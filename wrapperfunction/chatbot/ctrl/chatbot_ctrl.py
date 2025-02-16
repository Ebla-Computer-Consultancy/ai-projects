from wrapperfunction.chat_history.service.chat_history_service import upload_documents
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from fastapi import APIRouter, Depends, Request,UploadFile
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
from typing import List, Optional
from wrapperfunction.core import config
from wrapperfunction.function_auth.service import jwt_service

router = APIRouter()

@router.post("/chat/{bot_name}")
async def chat(request: Request,bot_name: str,message_payload: ChatPayload,token: str = Depends(jwt_service.get_token_from_header) if config.AUTH_ENABLED else None):
    return await chatbotservice.chat(bot_name,message_payload,request,token)

@router.post("/upload_documents/")
async def upload(files:List[UploadFile],request: Request,bot_name,conversation_id: Optional[str] = None):
    return await upload_documents(files,bot_name,request,conversation_id)
