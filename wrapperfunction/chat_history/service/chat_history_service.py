from typing import Optional
from wrapperfunction.core import config
from fastapi import HTTPException
from wrapperfunction.chat_history.model.message_entity import MessageEntity,MessagePropertyName
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity,ConversationPropertyName
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
import wrapperfunction.admin.integration.textanalytics_connector as text_connector




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
    
def get_messages(conversation_id):
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
    
async def add_entity(message_entity:MessageEntity,assistant_entity:MessageEntity,conv_entity:Optional[ConversationEntity] = None):
    try:
        if conv_entity:
            await db_connector.add_entity(config.CONVERSATION_TABLE_NAME,conv_entity.to_dict())
        await db_connector.add_entity(config.MESSAGE_TABLE_NAME,message_entity.to_dict())
        await db_connector.add_entity(config.MESSAGE_TABLE_NAME,assistant_entity.to_dict())

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
    
def perform_semantic_analysis():
    try:

        conversations = get_all_conversations()
        
        all_message_texts = ""  
        
        for conversation in conversations:
            if conversation[ConversationPropertyName.SENTIMENT.value] == "": 
                conversation_id = conversation[ConversationPropertyName.CONVERSATION_ID.value]
                messages = get_messages(conversation_id)
                message_texts = [msg[MessagePropertyName.CONTENT.value] for msg in messages if MessagePropertyName.CONTENT.value in msg]
                if not message_texts:
                    raise HTTPException(status_code=400, detail="No valid messages found for semantic analysis.")
                all_message_texts += " ".join(message_texts) + " "
                semantic_data = text_connector.analyze_sentiment([all_message_texts])
                update_conversation(conversation_id, {ConversationPropertyName.SENTIMENT.value: semantic_data})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



def perform_feedback_update(conversation_id: str, feedback: int):
    try:
        update_conversation(conversation_id, {ConversationPropertyName.FEEDBACK.value: feedback})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    