from wrapperfunction.chat_history.service.chat_history_service import upload_documents
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from fastapi import APIRouter, Request, HTTPException,UploadFile

from wrapperfunction.chatbot.model.third_user_model import ThirdUserAction
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
from typing import List, Optional

router = APIRouter()

@router.post("/chat/{bot_name}")
async def chat(request: Request,bot_name: str,message_payload: ChatPayload):
    return await chatbotservice.chat(bot_name,message_payload,request)

@router.post("/chat/{bot_name}/{third_user_type}/{action}")
async def action_investigation(bot_name: str,action:int, third_user_type:int ,message_payload: ChatPayload, request: Request):
    try:
        if action == ThirdUserAction.START.value:
            return await chatbotservice.start_three_users_conv(bot_name=bot_name, third_user_type=third_user_type, chat_payload=message_payload,request=request)
        elif action == ThirdUserAction.END.value:
            return await chatbotservice.end_three_users_conv(bot_name=bot_name, third_user_type=third_user_type, chat_payload=message_payload,request=request)
        elif action == ThirdUserAction.CONTINUE.value:
            return await chatbotservice.continue_three_users_conv(bot_name=bot_name, third_user_type=third_user_type, chat_payload=message_payload,request=request)
        elif action == ThirdUserAction.REPEAT.value:
            return await chatbotservice.repeat_question(bot_name=bot_name, third_user_type=third_user_type, chat_payload=message_payload,request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error While applying action: {action} is not a valid Action: {str(e)}")

@router.post("/upload_documents/")
async def upload(files:List[UploadFile],request: Request,bot_name,conversation_id: Optional[str] = None):
    return await upload_documents(files,bot_name,request,conversation_id)
