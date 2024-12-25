import asyncio
from typing import Optional
import uuid
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.core import config
from fastapi import HTTPException
from wrapperfunction.chat_history.model.message_entity import (
    MessageEntity,
    MessagePropertyName,
)
from wrapperfunction.chat_history.model.conversation_entity import (
    ConversationEntity,
    ConversationPropertyName,
)
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.core.model.service_return import ServiceReturn,StatusCode

import wrapperfunction.admin.integration.textanalytics_connector as text_connector
from wrapperfunction.chatbot.model.chat_message import Roles,MessageType
from wrapperfunction.interactive_chat.model.interactive_model import FormStatus




def get_conversations(user_id):
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME,f"{ConversationPropertyName.USER_ID.value} eq '{user_id}'")     
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def get_conversation_data(conversation_id):
    try:
        res=db_connector.get_entities(config.CONVERSATION_TABLE_NAME,f" {ConversationPropertyName.CONVERSATION_ID.value} eq '{conversation_id}'")     
        return res[0]
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


def get_messages(conversation_id):
    try:
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f"{MessagePropertyName.CONVERSATION_ID.value} eq '{conversation_id}'") 
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


def get_user_messages(conversation_id):
    try:
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f"{MessagePropertyName.CONVERSATION_ID.value} eq '{conversation_id}' and {MessagePropertyName.ROLE.value} eq '{Roles.User.value}' and {MessagePropertyName.MessageType.value} eq '{MessageType.Message.value}'") 
        return list(res)

    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


def get_all_conversations(bot_name: Optional[str] = None):
    try:
        filter_condition = f"{ConversationPropertyName.BOT_NAME.value} eq '{bot_name}'" if bot_name else None
        res = db_connector.get_entities(config.CONVERSATION_TABLE_NAME, filter_condition)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e)) 
    
async def add_entity(message_entity:Optional[MessageEntity]=None,assistant_entity:Optional[MessageEntity] = None,conv_entity:Optional[ConversationEntity] = None):
    try:
        if conv_entity:
            await db_connector.add_entity(config.CONVERSATION_TABLE_NAME,conv_entity.to_dict())
        if message_entity:    
            await db_connector.add_entity(config.MESSAGE_TABLE_NAME,message_entity.to_dict())    
        if assistant_entity:
            await db_connector.add_entity(config.MESSAGE_TABLE_NAME, assistant_entity.to_dict())




    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))   

    
def update_conversation(conversation_id: str, updated_data: dict):
    try:
        conversation = get_conversation_data(conversation_id)
        if conversation:
            conversation.update(updated_data)
            db_connector.update_entity(config.CONVERSATION_TABLE_NAME, conversation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def perform_sentiment_analysis():
    try:
        conversations = get_all_conversations()
        for conversation in conversations:
            if conversation[ConversationPropertyName.SENTIMENT.value] == "undefined" and conversation[ConversationPropertyName.BOT_NAME.value] != "interactive":
                conversation_id = conversation[
                    ConversationPropertyName.CONVERSATION_ID.value
                ]
                if not conversation_id:
                    continue
                messages = get_user_messages(conversation_id)
                message_texts = [
                    msg[MessagePropertyName.CONTENT.value]
                    for msg in messages
                    if MessagePropertyName.CONTENT.value in msg
                ]
                if not message_texts:
                    continue
                all_message_texts = " ".join(message_texts) + " "
                semantic_data = text_connector.analyze_sentiment([all_message_texts])
                
                update_conversation(
                    conversation_id,
                    {ConversationPropertyName.SENTIMENT.value: semantic_data},
                )
        return ServiceReturn(
            status=StatusCode.SUCCESS, message="analysis done successfully"
        ).to_dict()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def perform_feedback_update(conversation_id: str, feedback: int):
    try:
        update_conversation(
            conversation_id, {ConversationPropertyName.FEEDBACK.value: feedback}
        )
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

async def add_message(chat_payload: ChatPayload, bot_name: str):
    try:
        conv_id = chat_payload.conversation_id or str(uuid.uuid4())
        user_id = chat_payload.user_id or str(uuid.uuid4())
        if not chat_payload.conversation_id:
            title = chat_payload.messages[0].content[:20].strip()
            
            message_entity = MessageEntity(chat_payload.messages[0].content, conv_id, Roles.User.value, "")
            conv_entity = ConversationEntity(user_id, conv_id, bot_name, title)
            await add_entity(message_entity, None, conv_entity)  
        else:
            message_entity = MessageEntity(chat_payload.messages[0].content, conv_id, Roles.User.value, "")
            await add_entity(message_entity)  
        return ServiceReturn(
            status=StatusCode.SUCCESS, message="message added successfully", data=conv_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_all_vactions():
    try:
        res =  db_connector.get_entities(config.COSMOS_VACATION_TABLE)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def get_vactions_filter_by(coulomn_name,value):
    try:
        res =  db_connector.get_entities(config.COSMOS_VACATION_TABLE,f"{coulomn_name} eq {value}")
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def update_Status(employee_ID: str, status: int):
    try:
        forms = get_vactions_filter_by("Employee_ID",employee_ID)
        if forms:
            for form in forms:
                
                form.update({"Status":status,"Comments":f"{FormStatus(status).name} by Manager"})
                db_connector.update_entity(config.COSMOS_VACATION_TABLE, form)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def add_form(form: dict):
    try:
        await db_connector.add_entity(config.COSMOS_VACATION_TABLE,form)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))