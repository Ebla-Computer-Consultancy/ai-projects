from wrapperfunction.website.model.search_criterial import searchCriteria
from wrapperfunction.website.model.chat_payload import ChatPayload
from fastapi import APIRouter
import wrapperfunction.website.service.ws_service as wsservice
from typing import List

router = APIRouter()


@router.post("/search")
def search(rs: searchCriteria):
    return wsservice.search(rs)


@router.post("/chat")
async def search(message_payload: ChatPayload):
    return await wsservice.chat(message_payload)
