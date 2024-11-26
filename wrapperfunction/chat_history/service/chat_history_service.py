import json
import os
from typing import Optional
from wrapperfunction.core import config
from fastapi import HTTPException
from wrapperfunction.chat_history.model.message_entity import MessageEntity,MessagePropertyName
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity,ConversationPropertyName
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.core.model.service_return import ServiceReturn,StatusCode


import wrapperfunction.admin.integration.textanalytics_connector as text_connector

from wrapperfunction.chatbot.model.chat_message import Roles,MessageType





def get_conversations(user_id):
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME,f"{ConversationPropertyName.USER_ID.name} eq '{user_id}'")     
        return res
    except Exception as e:
        return HTTPException(400,e)

def get_conversation_data(conversation_id):
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME,f" {ConversationPropertyName.CONVERSATION_ID.value} eq '{conversation_id}'")     
        return res[0]
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))           
    
def get_messages(conversation_id):
    try:
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f" {MessagePropertyName.CONVERSATION_ID} eq '{conversation_id}'") 
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
def get_user_messages(conversation_id):
    try:

        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f"{MessagePropertyName.CONVERSATION_ID.value} eq '{conversation_id}' and {MessagePropertyName.ROLE.value} eq '{Roles.User.value}' and {MessagePropertyName.MessageType.value} eq '{MessageType.Message.value}'") 

    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def get_all_conversations(bot_name:Optional[str]=None):
    try:
        filter_condition = f"{ConversationPropertyName.BOT_NAME.value} eq '{bot_name}'" if bot_name else None
        res = db_connector.get_entities(config.CONVERSATION_TABLE_NAME, filter_condition)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e)) 
    
async def add_entity(message_entity:MessageEntity,assistant_entity:Optional[MessageEntity] = None,conv_entity:Optional[ConversationEntity] = None):
    try:
        if conv_entity:
            await db_connector.add_entity(config.CONVERSATION_TABLE_NAME,conv_entity.to_dict())
        if assistant_entity:
            await db_connector.add_entity(config.MESSAGE_TABLE_NAME,assistant_entity.to_dict())

        await db_connector.add_entity(config.MESSAGE_TABLE_NAME,message_entity.to_dict())
        

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
    
def perform_sentiment_analysis():
    try:
        conversations = get_all_conversations()
        for conversation in conversations:
            if conversation[ConversationPropertyName.SENTIMENT.value] == "undefined": 
                conversation_id = conversation[ConversationPropertyName.CONVERSATION_ID.value]
                messages = get_user_messages(conversation_id)
                message_texts = [msg[MessagePropertyName.CONTENT.value] for msg in messages if MessagePropertyName.CONTENT.value in msg]
                if not message_texts:
                    continue
                all_message_texts = " ".join(message_texts) + " "
                semantic_data = text_connector.analyze_sentiment([all_message_texts])
                update_conversation(conversation_id, {ConversationPropertyName.SENTIMENT.value: semantic_data})
        return ServiceReturn(
        status=StatusCode.SUCCESS, message="analysis done successfully"
    ).to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def perform_feedback_update(conversation_id: str, feedback: int):
    try:
        update_conversation(conversation_id, {ConversationPropertyName.FEEDBACK.value: feedback})
        return ServiceReturn(
        status=StatusCode.SUCCESS, message="feedback updated successfully"
    ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    
def get_bot_name():
    bot_names = []  
    try:
        ENTITY_SETTINGS = config.ENTITY_SETTINGS
        bot_names=[chatbot_obj["name"] for chatbot_obj in ENTITY_SETTINGS.get("chatbots", [])]
        return bot_names 
        

        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

        