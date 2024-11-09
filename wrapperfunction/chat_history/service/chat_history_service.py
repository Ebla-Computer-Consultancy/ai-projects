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
    
def get_chat_history(conversation_id):
    try:
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f" conversation_id eq '{conversation_id}'") 
        return list(res)
    except Exception as e:
        return HTTPException(400,e)


def get_all_conversations():
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME,"SELECT * FROM c") 
        return list(res)
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
    
def apply_analysis(conversation_id):
    try:
        db_connector.analyze_and_update_semantics(conversation_id)    
    except Exception as e:
        return HTTPException(400,e)  
def add_feedback(conversation_id,feedback:int):
    try:
        db_connector.update_feedback(conversation_id,feedback)
    except Exception as e:
        return HTTPException(400,e)  

    