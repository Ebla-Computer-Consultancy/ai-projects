from wrapperfunction.website.model.search_criterial import searchCriteria
from wrapperfunction.website.model.chat_payload import ChatPayload
from fastapi import APIRouter, HTTPException
import wrapperfunction.website.service.ws_service as wsservice
from wrapperfunction.database.cosmos_connector import CosmosDBConnector
from typing import List

router = APIRouter()

<<<<<<< HEAD:wrapperfunction/website/ctrl/ws_ctrl.py
=======
db_connector = CosmosDBConnector()
>>>>>>> 4a5de49 (adding endpoint to get chat history):api/wrapperfunction/website/ctrl/ws_ctrl.py

@router.post("/search")
def search(rs: searchCriteria):
    return wsservice.search(rs)


@router.post("/chat")
async def search(message_payload: ChatPayload):
    return await wsservice.chat(message_payload)
<<<<<<< HEAD:wrapperfunction/website/ctrl/ws_ctrl.py
=======
# The following code creates an endpoint to get chat history by User ID
# This handles fastAPI routing, using the cosmosDB to interact with the database.
@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    try:
        chat_history = db_connector.get_chat_history_by_user_id(user_id)
        if not chat_history:
            raise HTTPException(status_code=404, detail="Chat history not found")
        return chat_history
    except Exception as error:
        return {"error": True, "message": str(error)}
>>>>>>> 4a5de49 (adding endpoint to get chat history):api/wrapperfunction/website/ctrl/ws_ctrl.py
