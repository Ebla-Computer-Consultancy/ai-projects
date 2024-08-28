from wrapperfunction.website.model.search_criterial import searchCriteria
from wrapperfunction.website.model.chat_message import ChatMessage
from fastapi import APIRouter
import wrapperfunction.website.service.ws_service as wsservice
from typing import List

router = APIRouter()

@router.post("/search")
def search(rs: searchCriteria):
    return wsservice.search(rs)

@router.post("/chat")
def search(messageHistory: List[ChatMessage]):
    return wsservice.chat(messageHistory)