import asyncio
import json
import uuid
from fastapi import Request
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.model.chat_message import Roles
from wrapperfunction.chatbot.model.third_user_model import ThirdUserTypes
from wrapperfunction.core import config
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.avatar.integration.avatar_connector as avatar_connector
import wrapperfunction.chat_history.service.chat_history_service as chat_history_service
from wrapperfunction.core.model.entity_setting import ChatbotSetting
from wrapperfunction.core.utls.helper import extract_client_details

async def chat(bot_name: str, chat_payload: ChatPayload, request: Request):
    try:
        chatbot_settings, chat_history_with_system, conversation_id = before_response_setup(bot_name, chat_payload, request)

        # Get response from OpenAI ChatGPT
        results = openaiconnector.chat_completion(
            chatbot_settings, chat_history_with_system
        )

        results = after_response_setup(results,bot_name, chatbot_settings,conversation_id, chat_payload)
        return results

    except Exception as error:
        return {"error": True, "message": str(error)}

def before_response_setup(bot_name: str, chat_payload: ChatPayload, request: Request):
            client_details = extract_client_details(request)
            conversation_id = chat_payload.conversation_id or str(uuid.uuid4())
            chat_history_with_system = prepare_chat_history_with_system_message(chat_payload, bot_name)
            chatbot_settings = config.load_chatbot_settings(bot_name)

            if chatbot_settings.enable_history:
                chat_history_service.save_history(
                    Roles.User.value,chat_payload, conversation_id, bot_name, client_details, chat_history_with_system
                )
            return chatbot_settings,chat_history_with_system["chat_history"], conversation_id
        
def after_response_setup(results, bot_name: str, chatbot_settings: ChatbotSetting,conversation_id: str, chat_payload:ChatPayload):
        if chatbot_settings.enable_history:
            chat_history_service.save_history(
                role=Roles.Assistant.value,results=results, conversation_id=conversation_id, chat_payload=chat_payload, bot_name=bot_name
            )
        if chat_payload.stream_id is not None and results["message"]["content"] is not None:
            is_ar = is_arabic(results["message"]["content"][:30])
            # await avatar connector.render_text_async(chat_payload.stream_id,results['message']['content'], is_ar)
            asyncio.create_task(
                avatar_connector.render_text_async(
                    chat_payload.stream_id, results["message"]["content"], is_ar
                )
            )            

        results["message"]["conversation_id"] = conversation_id
        return results

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
            "".join(results["message"]["content"].replace("\n", "").split()).strip(),
        )
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


def prepare_chat_history_with_system_message(chat_payload, bot_name):
    chat_history_arr = []
    bot_settings = config.load_chatbot_settings(bot_name)
    if bot_settings.custom_settings.max_history_length != 0:
        if chat_payload.conversation_id:
            chat_history_arr = chat_history_service.get_messages(
                conversation_id=chat_payload.conversation_id
            )
        if bot_settings.custom_settings.max_history_length > 0:
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
            msg["content"] = json.dumps(tool,ensure_ascii=False)
        chat_history.append(msg)        
    chat_history.append(chat_payload.messages[-1].model_dump())

    return {"system_message": system_message, "chat_history": chat_history}


def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)


async def start_three_users_conv(bot_name:str, chat_payload: ChatPayload, third_user_type: int, request: Request):
    try:
        chatbot_settings, chat_history_with_system, conversation_id = before_response_setup(bot_name, chat_payload, request)
        chat_history = [{"role":"system","content":chatbot_settings.system_message},{"role":"user","content":f"{ThirdUserTypes(third_user_type).name}: " + chat_payload.messages[-1].content + " Note: Response with the language you used to talk with in the conversation"}]
        
        # Get response from OpenAI ChatGPT
        results = openaiconnector.chat_completion(
            chatbot_settings, chat_history=chat_history
        )

        return after_response_setup(results,bot_name, chatbot_settings,conversation_id, chat_payload)

    except Exception as error:
        return json.dumps({"error": True, "message": f"Error while starting three user conversation: {str(error)}"})

async def end_three_users_conv(bot_name:str, chat_payload: ChatPayload, third_user_type: int, request: Request):
    try:
        if chat_payload.conversation_id:
            chat_history_with_system_message = prepare_chat_history_with_system_message(
            chat_payload, bot_name
            )

            conversation_id = chat_payload.conversation_id
            chatbot_settings = config.load_chatbot_settings(bot_name)
            chat_history = chat_history_with_system_message["chat_history"]
            third_user_history = prepare_third_user_chat_history(chat_payload)
            third_user_history.append({"role":"user","content":f"{ThirdUserTypes(third_user_type).name}: Conversation is over. Note: Response with the language you used to talk with in the conversation"})
            full_history = list(chat_history) + third_user_history
            # Get response from OpenAI ChatGPT
            results = openaiconnector.chat_completion(
                chatbot_settings, chat_history=full_history
            )
            
            return after_response_setup(results,bot_name, chatbot_settings,conversation_id, chat_payload)
        else:
            return json.dumps({"error": True, "message": f"Error while ending three user conversation: conversation_id is require to end the conversation"})

    except Exception as error:
        return json.dumps({"error": True, "message": f"Error while ending three user conversation: {str(error)}"})

async def continue_three_users_conv(bot_name:str, chat_payload: ChatPayload, third_user_type: int, request: Request):
    try:
        client_details = extract_client_details(request)
        if chat_payload.conversation_id:
            chat_history_with_system_message = prepare_chat_history_with_system_message(
            chat_payload, bot_name
            )

            conversation_id = chat_payload.conversation_id
            chatbot_settings = config.load_chatbot_settings(bot_name)
            chat_history = chat_history_with_system_message["chat_history"]
            chat_history.append({"role":"user","content":f"{ThirdUserTypes(third_user_type).name}: Continue. Note: Response with the language you used to talk with in the conversation"})
            # Get response from OpenAI ChatGPT
            results = openaiconnector.chat_completion(
                chatbot_settings, chat_history=chat_history
            )
            
            return after_response_setup(results,bot_name, chatbot_settings,conversation_id, chat_payload)
        else:
            return json.dumps({"error": True, "message": f"Error while Completing three user conversation: conversation_id is required to continue the conversation"})

    except Exception as error:
        return json.dumps({"error": True, "message": f"Error while Completing three user conversation: {str(error)}"})

async def repeat_question(bot_name:str, chat_payload: ChatPayload, third_user_type: int, request: Request):
    try:
        client_details = extract_client_details(request)
        if chat_payload.conversation_id:
            chat_history_with_system_message = prepare_chat_history_with_system_message(
            chat_payload, bot_name
            )

            conversation_id = chat_payload.conversation_id
            chatbot_settings = config.load_chatbot_settings(bot_name)
            chat_history = chat_history_with_system_message["chat_history"]
            chat_history.append({"role":"user","content":f"{ThirdUserTypes(third_user_type).name}: Ask this question Again ({chat_payload.messages[-1].content}). Note: Response with the language you used to talk with in the conversation"})
            # Get response from OpenAI ChatGPT
            results = openaiconnector.chat_completion(
                chatbot_settings, chat_history=chat_history
            )
            
            return after_response_setup(results,bot_name, chatbot_settings,conversation_id, chat_payload)
        else:
            return json.dumps({"error": True, "message": f"Error while Repeating question: conversation_id is required to repeat"})

    except Exception as error:
        return json.dumps({"error": True, "message": f"Error while Repeating question: {str(error)}"})
    
def prepare_third_user_chat_history(chat_payload: ChatPayload):
    third_user_history = []
    for msg in chat_payload.messages:
        third_user_history.append({"role": msg.role,"content":msg.content})
    return third_user_history 
