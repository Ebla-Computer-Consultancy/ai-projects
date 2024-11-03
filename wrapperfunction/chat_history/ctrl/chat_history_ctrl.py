from fastapi import APIRouter
import wrapperfunction.chat_history.integration.cosmos_db_connector as historyservice


router = APIRouter()

@router.get("/get-all-chats/")
def get_chats(user_id: str):
    return historyservice.get_all_conversations(user_id)


@router.get("/get-chat/")
def get_chats(conv_id: str):
    return historyservice.get_chat_history(conv_id)

