from typing import Optional
from wrapperfunction.core import config
from fastapi import HTTPException
from wrapperfunction.chat_history.model.message_entity import MessageEntity
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector



def get_conversations(user_id):
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME,f"user_id eq '{user_id}'")     
        return res
    except Exception as e:
        return HTTPException(400,e)

def get_conversation_data(conversation_id):
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME,f" conversation_id eq '{conversation_id}'")     
        return res[0]
    except Exception as e:
        return HTTPException(400,e)           
    
def get_chat_history(conversation_id):
    try:
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f" conversation_id eq '{conversation_id}'") 
        return list(res)
    except Exception as e:
        return HTTPException(400,e)


def get_all_conversations():
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME) 
        return res
    except Exception as e:
        return HTTPException(400,e) 
    
async def add_history(message_entity:MessageEntity,assistant_entity:MessageEntity,conv_entity:Optional[ConversationEntity] = None):
    try:
        await db_connector.add_to_history(config.MESSAGE_TABLE_NAME,message_entity.to_dict())
        await db_connector.add_to_history(config.MESSAGE_TABLE_NAME,assistant_entity.to_dict())
        if conv_entity:
            await db_connector.add_to_history(config.CONVERSATION_TABLE_NAME,conv_entity.to_dict())
    except Exception as e:
        return HTTPException(400,e)    
    
def update_conversation(conversation_id: str, updated_data: dict):
    try:
        conversation = get_conversation_data(conversation_id)
        if conversation: 
            conversation.update(updated_data) 
            db_connector.update_entity(config.CONVERSATION_TABLE_NAME,conversation) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))