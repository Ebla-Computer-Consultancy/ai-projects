from typing import Optional, Dict, Any
from wrapperfunction.core import config
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException
from azure.ai.textanalytics import TextAnalyticsClient
import os

table_service_client = TableServiceClient.from_connection_string(conn_str=config.CONNECTION_STRING)
endpoint = config.AZURE_TEXT_ANALYTICS_ENDPOINT
api_key = config.AZURE_TEXT_ANALYTICS_KEY
text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

class GenericTableClient:
    def __init__(self, table_name: str):
        self.table_client = table_service_client.get_table_client(table_name=table_name)

    async def add_entity(self, entity: Dict[str, Any]) -> None:
        try:
            self.table_client.create_entity(entity)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_entities(self, filter_expression: Optional[str] = None) -> list:
        try:
            if filter_expression:
                entities = self.table_client.query_entities(filter_expression)
            else:
                entities = self.table_client.list_entities()
            return list(entities)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def update_entity(self, entity: Dict[str, Any]) -> None:
        try:
            self.table_client.update_entity(entity, mode=UpdateMode.MERGE)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

async def add_to_history(table_name: str, entity: Dict[str, Any]):
    generic_table_client = GenericTableClient(table_name)
    await generic_table_client.add_entity(entity)

def get_entities(table_name: str, filter_expression: Optional[str] = None):
    generic_table_client = GenericTableClient(table_name)
    return generic_table_client.get_entities(filter_expression)

def analyze_and_update_semantics(conversation_id: str):
    try:
        message_client = GenericTableClient(config.MESSAGE_TABLE_NAME)
        messages = message_client.get_entities(f"conversation_id eq '{conversation_id}'")   
        message_texts = [msg["content"] for msg in messages if "content" in msg] 
        if not message_texts:
            raise HTTPException(status_code=400, detail="No valid messages found for semantic analysis.")
        sentiment_response = text_analytics_client.analyze_sentiment(message_texts)[0]
        semantic_data = sentiment_response.sentiment
        conversation_client = GenericTableClient(config.CONVERSATION_TABLE_NAME)
        conversations = conversation_client.get_entities(f"conversation_id eq '{conversation_id}'")
        if conversations:
            conversation = conversations[0]  
            conversation["sentiment"] = semantic_data  
            conversation_client.update_entity(conversation) 
        
        return semantic_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_feedback(conversation_id: str, feedback: int):
    try:     
        conversation_client = GenericTableClient(config.CONVERSATION_TABLE_NAME)
        conversations = conversation_client.get_entities(f"conversation_id eq '{conversation_id}'")
        if not conversations:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        conversation = conversations[0]
        conversation["feedback"] = feedback
        conversation_client.update_entity(conversation)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
