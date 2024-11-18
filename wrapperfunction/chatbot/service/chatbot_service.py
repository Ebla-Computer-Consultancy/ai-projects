import asyncio
import json
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.model.chat_message import Roles
from wrapperfunction.core import config
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.avatar.integration.avatar_connector as avatarconnector
from fastapi import status, HTTPException
from wrapperfunction.chat_history.model.message_entity import MessageEntity
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity
import wrapperfunction.chat_history.service.chat_history_service as chat_history_service 
import uuid


async def chat(bot_name: str, chat_payload: ChatPayload):
    try:
        chat_history_with_system_message = prepare_chat_history_with_system_message(
            chat_payload, bot_name
        )
        
        conversation_id = chat_payload.conversation_id or str(uuid.uuid4())   
        chatbot_settings = config.load_chatbot_settings(bot_name)
        chatbot_settings.system_message = chat_history_with_system_message[
            "system_message"
        ]
        # Get response from OpenAI ChatGPT
        results = openaiconnector.chat_completion(
            chatbot_settings, chat_history_with_system_message["chat_history"]
        )
        #Set user message
        user_message_entity = set_user_message(conversation_id, chat_history_with_system_message["chat_history"][-1]["content"])
        #Set assistant or Tool message
        tools_message_entity = None
        assistant_message_entity = None
        if results["message"]["tool_calls"]:
            tools_message_entity = set_tool_message(conversation_id,results["message"]["tool_calls"])
        else:
            assistant_message_entity = set_assistant_message(conversation_id, results["message"]["content"])
        
        # Add Messages
        add_all_messages_to_Entity(
            chat_payload=chat_payload,
            conversation_id=conversation_id,
            user_message_entity=user_message_entity,
            assistant_message_entity=assistant_message_entity,
            bot_name=bot_name,
            tools_message_entity= tools_message_entity        
                    )
        
        if chat_payload.stream_id is not None:
            is_ar = is_arabic(results["message"]["content"][:30])
            # await avatarconnector.render_text_async(chat_payload.stream_id,results['message']['content'], is_ar)
  
            asyncio.create_task(
                avatarconnector.render_text_async(
                    chat_payload.stream_id, results["message"]["content"], is_ar
                )
                
            )

        results["message"]["conversation_id"] = conversation_id
        return results

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})
    
def set_user_message(conversation_id,content):
    # Set user message Entity
    return MessageEntity(
        conversation_id=conversation_id,
            content=content,  
            role=Roles.User.value,)
def set_assistant_message(conversation_id,content):
    # Set user message Entity
    return MessageEntity(
        conversation_id=conversation_id,
            content=content,  
            role=Roles.Assistant.value,)
def set_tool_message(conversation_id,tool_calls):
    # Set user message Entity
    return [MessageEntity(
            conversation_id=conversation_id,
            content=json.dumps(tool_call),  
            role=Roles.Tool.value) for tool_call in tool_calls]
    
def add_all_messages_to_Entity(
        chat_payload,
        conversation_id,
        user_message_entity,
        bot_name,
        assistant_message_entity = None,
        tools_message_entity = None
        ):
    
    user_id = chat_payload.user_id or str(uuid.uuid4())
    
    # Set Convertsation Entity
    conv_entity=ConversationEntity(user_id, conversation_id,bot_name)
    
    if not tools_message_entity:
        if not chat_payload.conversation_id:
            add_message_to_Entity_with_conv(
                    user_message_entity,assistant_message_entity,conv_entity
                    )
        else:
            add_message_to_Entity(user_message_entity,assistant_message_entity)
                
    else:
        for tool_message in tools_message_entity:
            if not chat_payload.conversation_id:
                add_message_to_Entity_with_conv(
                    user_message_entity,tool_message,conv_entity
                    )
            else:
                add_message_to_Entity(user_message_entity,tool_message)
        
def add_message_to_Entity(user_message_entity,assistant_message_entity):
    asyncio.create_task(
                    chat_history_service.add_entity(user_message_entity,assistant_message_entity),
                )
    
def add_message_to_Entity_with_conv(user_message_entity,assistant_message_entity,conv_entity):
    asyncio.create_task(
                    chat_history_service.add_entity(
                    user_message_entity,assistant_message_entity,conv_entity
                    ),
                )            
def ask_open_ai_chatbot(bot_name: str, chat_payload: ChatPayload):
    try:
        chat_history_with_system_message = prepare_chat_history_with_system_message(
            chat_payload, bot_name
        )
        chatbot_settings = config.load_chatbot_settings(bot_name)
        # Get response from OpenAI ChatGPT
        results = openaiconnector.chat_completion(
            chatbot_settings,
            chat_history=chat_history_with_system_message["chat_history"],
        )
        return results
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


def prepare_chat_history_with_system_message(chat_payload, bot_name):
    
    chat_history_arr = chat_history_service.get_messages(conversation_id=chat_payload.conversation_id)
    
    if bool(len([x for x in chat_history_arr if x["role"] == "system"])):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "system messages is not allowed"
        )
    chat_history = []
    is_ar = is_arabic(chat_history_arr[-1]["content"])
    if chat_payload.stream_id:
        if is_ar:
            system_message = f"IMPORTANT: Represent numbers in alphabet only not numeric. Always respond with very short answers. {config.load_chatbot_settings(bot_name).system_message}"
        else:
            system_message = f"{config.load_chatbot_settings(bot_name).system_message}, I want you to detect the input language and responds in the same language. Always respond with very short answers."
    else:
        system_message = f"{config.load_chatbot_settings(bot_name).system_message}, I want you to detect the input language and responds in the same language."

    system_message += " If user asked you about a topic outside your knowledge, never answer but suggest relevant resources or someone knowledgeable."
    chat_history.insert(0, {"role": Roles.System.value, "content": system_message})
    for item in chat_history_arr:
        msg = {"role": item["role"],"content":item["content"]}
        if item["role"] == "tool":
            tool = json.loads(item["content"])
            tool["id"] = chat_payload.conversation_id
            tool["function"]["arguments"] = json.dumps(tool["function"]["arguments"])
            chat_history.append({"role": "assistant",
                                 "tool_calls":[
                                     tool
                                     ]
                                 })
            msg["tool_call_id"] = chat_payload.conversation_id
        chat_history.append(msg)
    chat_history.append(chat_payload.messages[-1].model_dump())
    return {"system_message": system_message, "chat_history": chat_history}


def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)