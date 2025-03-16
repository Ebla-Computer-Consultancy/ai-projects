import asyncio
import datetime
import json
import traceback
from typing import Optional
import uuid
from fastapi import Request
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.model.chat_message import MessageType, Roles
from wrapperfunction.core import config
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.avatar.integration.avatar_connector as avatar_connector
import wrapperfunction.chat_history.service.chat_history_service as chat_history_service
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.core.utls.helper import extract_client_details
from wrapperfunction.document_intelligence.integration.document_intelligence_connector import analyze_file
from wrapperfunction.function_auth.service import jwt_service
from wrapperfunction.chat_history.model.message_entity import MessageEntity
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity 


async def chat(bot_name: str, chat_payload: ChatPayload, request: Request):
    try:
        token = jwt_service.get_token(request)
        user_data = jwt_service.decode_jwt(token, clear_payload=True) if token else None
        user_message_id = str(uuid.uuid4())
        client_details = extract_client_details(request)
        conversation_id = chat_payload.conversation_id or str(uuid.uuid4())
        chat_history_with_system = prepare_chat_history_with_system_message(chat_payload, bot_name, user_data)
        chatbot_settings = config.load_chatbot_settings(bot_name)
        category_result = None
        if chatbot_settings.custom_settings.categorize:
            category_result = categorize_query(chat_payload.messages[-1].content, bot_name)
            chatbot_settings.custom_settings.filter_exp=f"search.ismatch('{category_result}', '{chatbot_settings.custom_settings.categorize_field}') or search.ismatchscoring('{category_result}')"
            
        
        if chatbot_settings.enable_history:
            chat_history_service.save_history(
                Roles.User.value, chat_payload, conversation_id, user_message_id, bot_name, None, client_details, chat_history_with_system
            )

        results = openaiconnector.chat_completion(
            chatbot_settings, chat_history_with_system["chat_history"], category_result
        )
        if chatbot_settings.enable_history:
            chat_history_service.save_history(
                role=Roles.Assistant.value, results=results, question_id=user_message_id, 
                message_id=str(uuid.uuid4()), conversation_id=conversation_id, 
                chat_payload=chat_payload, bot_name=bot_name
            )

        if chat_payload.stream_id and results["message"]["content"]:
            is_ar = is_arabic(results["message"]["content"][:30])
            asyncio.create_task(
                avatar_connector.render_text_async(chat_payload.stream_id, results["message"]["content"], is_ar)
            )

        results["message"]["conversation_id"] = conversation_id
        return results

    except Exception as error:
        asyncio.create_task(chat_history_service.log_error_to_db(str(error), traceback.format_exc(), conversation_id, user_message_id))
        return {"error": True, "message": str(error)}

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
        return (
            " ".join(results["message"]["content"].replace("\n", " ").split()),
        )
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


def prepare_chat_history_with_system_message(chat_payload, bot_name, user_data = None):
    chat_history_arr = []
    bot_settings = config.load_chatbot_settings(bot_name)
    date = datetime.datetime.now().date()
    if bot_settings.custom_settings.max_history_length != 0:
        if chat_payload.conversation_id:
            chat_history_arr = chat_history_service.get_messages(
                conversation_id=chat_payload.conversation_id
            )

        if bot_settings.custom_settings.max_history_length > 0:
            if bot_settings.preserve_first_message and chat_history_arr:
                first_message = chat_history_arr[0]
                chat_history_arr = chat_history_arr[-bot_settings.custom_settings.max_history_length:]
                if first_message not in chat_history_arr:
                    chat_history_arr.insert(0, first_message)
            else:
                chat_history_arr = chat_history_arr[-bot_settings.custom_settings.max_history_length:]

    chat_history = []
    is_ar = is_arabic(chat_payload.messages[-1].content)
    if chat_payload.stream_id:
        if is_ar:
            system_message = f"IMPORTANT: Represent numbers in alphabet only not numeric. Always respond with very short answers. {config.load_chatbot_settings(bot_name).system_message}"
        else:
            system_message = f"{bot_settings.system_message}, I want you to detect the input language and responds in the same language. Always respond with very short answers."
    else:
        system_message = f"{bot_settings.system_message}, I want you to detect the input language and responds in the same language."
    system_message += " If user asked you about a topic outside your knowledge, never answer but suggest relevant resources or someone knowledgeable."
    if user_data:
        system_message += f" You are talking to following user: {user_data}. today date:{date}"
    chat_history.insert(0, {"role": Roles.System.value, "content": system_message})

    chat_history.extend(bot_settings.examples)
    
    for item in chat_history_arr:
        msg = {"role": item["role"], "content": item["content"]}
        if (
            bot_settings.custom_settings.tools
            and item["role"] == "tool"
        ):
            tool = json.loads(item["content"])
            tool["id"] = chat_payload.conversation_id
            tool["function"]["arguments"] = json.dumps(tool["function"]["arguments"], ensure_ascii=False)
            chat_history.append({"role": "assistant", "tool_calls": [tool]})
            msg["tool_call_id"] = chat_payload.conversation_id
        chat_history.append(msg)
    chat_history.append(chat_payload.messages[-1].model_dump())

    return {"system_message": system_message, "chat_history": chat_history}



def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)
def categorize_query(query: str, bot_name: str) -> str:

    try:
        chatbot_settings = config.load_chatbot_settings(bot_name)
        prompt = [
            {"role": "system", "content": chatbot_settings.custom_settings.categorize},
            {"role": "user", "content": query}
        ]
        chatbot_settings.index_name = None
        result = openaiconnector.chat_completion(chatbot_settings, prompt)
        category = result.get("message", {}).get("content", "").strip() if result else None
        return category if category in chatbot_settings.custom_settings.categorize else None
    except Exception:
        return None

def get_openai_instruction(prompt, bot_name):
    chatbot_settings=config.load_chatbot_settings(bot_name)
    chat_history = [
        {"role": "system", "content": chatbot_settings.system_message},
        {"role": "user", "content": prompt}
    ]
    try:
        response = openaiconnector.chat_completion(chatbot_settings, chat_history)
       
        return response['message']['content']
    except Exception as e:
        return {"error": f"Error with Azure OpenAI API: {e}"}