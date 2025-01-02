import asyncio
import json
from typing import Optional
from urllib.request import Request
import uuid

from user_agents import parse
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
from wrapperfunction.document_intelligence.integration.document_intelligence_connector import analyze_file
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

def get_all_vacations():
    try:
        res =  db_connector.get_entities(config.COSMOS_VACATION_TABLE)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def get_vacations_filter_by(column_name,value):
    try:
        res =  db_connector.get_entities(config.COSMOS_VACATION_TABLE,f"{column_name} eq {value}")
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def update_Status(employee_ID: str, status: int):
    try:
        forms = get_vacations_filter_by("Employee_ID",employee_ID)
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
async def upload_documents(files, bot_name, conversation_id: Optional[str] = None):
    try:
        content = ""
        for file in files:
            extracted_text = analyze_file(file, model_id='prebuilt-read').content
            content += extracted_text
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            title = content[:20].strip()

            user_message_entity = MessageEntity(content=content, conversation_id=conversation_id, role=Roles.User.value, context="", type=MessageType.Document.value)
            conv_entity = ConversationEntity(user_id=str(uuid.uuid4()), conversation_id=conversation_id, bot_name=bot_name, title=title)
            await add_entity(message_entity=user_message_entity, conv_entity=conv_entity)
        else:
            user_message_entity = MessageEntity(content=content, conversation_id=conversation_id, role=Roles.User.value, context="", type=MessageType.Document.value)

            await add_entity(message_entity=user_message_entity)

        return ServiceReturn(
            status=StatusCode.SUCCESS, message="file uploaded successfully", data=conversation_id
        ).to_dict()

    except Exception as e:
        return ServiceReturn(
            status=StatusCode.INTERNAL_SERVER_ERROR, message=f"Error occurred: {str(e)}"
        ).to_dict()
def extract_client_details(request: Request) -> dict:
    client_ip = request.client.host if request.client else "Unknown"
    forwarded_ip = request.headers.get("X-Forwarded-For", "Unknown")
    user_agent = request.headers.get("User-Agent", "")
    user_agent_parsed = parse(user_agent)
    device_info = {
        "browser": user_agent_parsed.browser.family,
        "os": user_agent_parsed.os.family,
        "device_type": user_agent_parsed.device.family,
    }
    return {
        "client_ip": client_ip,
        "forwarded_ip": forwarded_ip,
        "device_info": device_info,
    }        
def set_context(results):
    try:
        context = results["message"].get("context")
        if context:
            if isinstance(context, str):
                parsed_data = json.loads(context)
            elif isinstance(context, dict):
                parsed_data = context
            else:
                return json.dumps({"error": True, "message": "Invalid context format"})

            if isinstance(parsed_data.get("intent"), str):
                parsed_data["intent"] = json.loads(parsed_data["intent"])

            return json.dumps(parsed_data, ensure_ascii=False)
        if results["message"].get("tool_calls"):
            return ""
        return ""
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})

def set_message(conversation_id, role, content=None, tool_calls=None, context=None, completion_tokens=None, prompt_tokens=None, total_tokens=None):
    if role is not Roles.Tool.value:
        return MessageEntity(
            conversation_id=conversation_id,
            content=content,
            role=role,
            context=context,
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
        )
    return [
        MessageEntity(
            conversation_id=conversation_id,
            content=json.dumps(tool_call, ensure_ascii=False),
            role=Roles.Tool.value,
            context=context,
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
        )
        for tool_call in tool_calls
    ]

def add_messages_to_history(
    chat_payload,
    conversation_id,
    bot_name,
    user_message_entity=None,
    assistant_message_entity=None,
    tools_message_entity=None,
    client_ip=None,
    forwarded_ip=None,
    device_info=None,
):
    if tools_message_entity:
        handle_tool_messages(chat_payload, conversation_id, user_message_entity, tools_message_entity)
    else:
        handle_user_or_assistant_messages(
            chat_payload, conversation_id, bot_name, user_message_entity, assistant_message_entity, client_ip, forwarded_ip, device_info
        )

def save_user_message(chat_payload, conversation_id, bot_name, client_details, chat_history_with_system):
    user_message_entity = set_message(
        conversation_id=conversation_id,
        content=chat_history_with_system["chat_history"][-1]["content"],
        role=Roles.User.value,
    )

    add_messages_to_history(
        chat_payload=chat_payload,
        conversation_id=conversation_id,
        bot_name=bot_name,
        user_message_entity=user_message_entity,
        client_ip=client_details["client_ip"],
        forwarded_ip=client_details["forwarded_ip"],
        device_info=json.dumps(client_details["device_info"]),
    )
def create_and_add_message(chat_payload, conversation_id, user_message_entity, bot_name=None, client_ip=None, forwarded_ip=None, device_info=None):

    conv_entity = create_conversation_entity(
        chat_payload, conversation_id, user_message_entity, bot_name, client_ip, forwarded_ip, device_info
    )
    add_message_to_Entity(user_message_entity=user_message_entity, conv_entity=conv_entity)

def handle_tool_messages(
    chat_payload, 
    conversation_id, 
    user_message_entity, 
    tools_message_entity
):
    if not chat_payload.conversation_id and user_message_entity:
        create_and_add_message(chat_payload, conversation_id, user_message_entity)
    else:
        for tool_message in tools_message_entity:
            add_message_to_Entity(user_message_entity=user_message_entity, assistant_message_entity=tool_message)

def handle_user_or_assistant_messages(
    chat_payload, 
    conversation_id, 
    bot_name, 
    user_message_entity, 
    assistant_message_entity, 
    client_ip, 
    forwarded_ip, 
    device_info
):
    if not chat_payload.conversation_id and user_message_entity:
        create_and_add_message(
            chat_payload, 
            conversation_id, 
            user_message_entity, 
            bot_name, 
            client_ip, 
            forwarded_ip, 
            device_info
        )
    else:
        add_message_to_Entity(user_message_entity=user_message_entity, assistant_message_entity=assistant_message_entity)

def create_conversation_entity(chat_payload, conversation_id, user_message_entity, bot_name=None, client_ip=None, forwarded_ip=None, device_info=None):
    user_id = chat_payload.user_id or str(uuid.uuid4())
    title = user_message_entity.content[:20].strip()
    return ConversationEntity(
        user_id=user_id,
        conversation_id=conversation_id,
        bot_name=bot_name,
        title=title,
        client_ip=client_ip,
        forwarded_ip=forwarded_ip,
        device_info=device_info,
    )

def add_message_to_Entity(user_message_entity=None, assistant_message_entity=None, conv_entity=None):
    if conv_entity and user_message_entity:
        asyncio.create_task(
            add_entity(message_entity=user_message_entity, conv_entity=conv_entity)
        )
    else:
        asyncio.create_task(
            add_entity(
                message_entity=user_message_entity, assistant_entity=assistant_message_entity
            )
        )    