from fastapi import APIRouter
import wrapperfunction.chat_history.service.chat_history_service as historyservice


router = APIRouter()

@router.get("/get-conversations/")
def get_chats(user_id: str):
    return historyservice.get_conversations(user_id)
@router.get("/get-chat/")
def get_chats(conv_id: str):
    return historyservice.get_chat_history(conv_id)


@router.get("/get-all-conversations/")
def get_chats():
    return historyservice.get_all_conversations()

@router.post("/semantic_analysis/")
def apply_analysis():
    return historyservice.perform_semantic_analysis()
@router.post("/add_feedback/")
def add_feedback(conv_id: str, feedback: int):
    return historyservice.perform_feedback_update(conv_id, feedback)





