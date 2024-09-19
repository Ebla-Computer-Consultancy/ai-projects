from wrapperfunction.website.model.search_criterial import searchCriteria
from wrapperfunction.website.model.chat_payload import ChatPayload
from fastapi import APIRouter, HTTPException
import wrapperfunction.website.service.ws_service as wsservice
from wrapperfunction.core import config
from typing import List
import os
from azure.data.tables import TableServiceClient
from azure.core.exceptions import HttpResponseError

connection_string=config.CONNECTION_STRING
table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)

table_client = table_service_client.get_table_client(config.CONTAINER_NAME)

router = APIRouter()

@router.post("/search")
def search(rs: searchCriteria):
    return wsservice.search(rs)

@router.post("/chat")
async def search(message_payload: ChatPayload):
    return await wsservice.chat(message_payload)

#the following code Creates an endpoint to Get chat history by User ID
@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    try:
        query_filter = f"PartitionKey eq '{user_id}'"

        # Retrieve chat history based on the user_id
        chat_history = list(table_client.query_entities(config.CONTAINER_NAME, filter=query_filter))

        if not chat_history:
            raise HTTPException(status_code=404, detail="Chat history not found")

        return chat_history
    
    except HttpResponseError as cosmos_error:
        return {"error": True, "message": f"Cosmos DB Table API error: {str(cosmos_error)}"}
    except Exception as error:
        return {"error": True, "message": str(error)}