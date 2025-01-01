import asyncio
import json
import uuid
from fastapi import Request
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.model.chat_message import Roles
from wrapperfunction.core import config
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.avatar.integration.avatar_connector as avatar_connector
import wrapperfunction.chat_history.service.chat_history_service as chat_history_service

async def chat(bot_name: str, chat_payload: ChatPayload, request: Request):
    try:
        client_details = chat_history_service.extract_client_details(request)
        conversation_id = chat_payload.conversation_id or str(uuid.uuid4())
        chat_history_with_system = prepare_chat_history_with_system_message(chat_payload, bot_name)
        chatbot_settings = config.load_chatbot_settings(bot_name)

        if chatbot_settings.enable_history:
            save_user_message(
                chat_payload, conversation_id, bot_name, client_details, chat_history_with_system
            )
            # Get response from OpenAI ChatGPT
            results = openaiconnector.chat_completion(
                chatbot_settings, chat_history_with_system["chat_history"]
            )
            process_chatbot_response(
                results, conversation_id, chat_payload, bot_name
            )
        else:
            # Get response from OpenAI ChatGPT
            results = openaiconnector.chat_completion(
                chatbot_settings, chat_history_with_system["chat_history"]
            )

        results["message"]["conversation_id"] = conversation_id
        return results

    except Exception as error:
        return {"error": True, "message": str(error)}
def save_user_message(chat_payload, conversation_id, bot_name, client_details, chat_history_with_system):
    user_message_entity = chat_history_service.set_message(
        conversation_id=conversation_id,
        content=chat_history_with_system["chat_history"][-1]["content"],
        role=Roles.User.value,
    )

    chat_history_service.add_messages_to_history(
        chat_payload=chat_payload,
        conversation_id=conversation_id,
        bot_name=bot_name,
        user_message_entity=user_message_entity,
        client_ip=client_details["client_ip"],
        forwarded_ip=client_details["forwarded_ip"],
        device_info=json.dumps(client_details["device_info"]),
    )

def process_chatbot_response(results, conversation_id, chat_payload, bot_name):
    context = chat_history_service.set_context(results)
    tools_message_entity = None
    assistant_message_entity = None

    if results["message"].get("tool_calls"):
        tools_message_entity = chat_history_service.set_message(
            conversation_id=conversation_id,
            role=Roles.Tool.value,
            tool_calls=results["message"]["tool_calls"],
            context=context,
            completion_tokens=results["usage"]["completion_tokens"],
            prompt_tokens=results["usage"]["prompt_tokens"],
            total_tokens=results["usage"]["total_tokens"],
        )
    else:
        assistant_message_entity = chat_history_service.set_message(
            conversation_id=conversation_id,
            content=results["message"]["content"],
            role=Roles.Assistant.value,
            context=context,
            completion_tokens=results["usage"]["completion_tokens"],
            prompt_tokens=results["usage"]["prompt_tokens"],
            total_tokens=results["usage"]["total_tokens"],
        )

    chat_history_service.add_messages_to_history(
        chat_payload=chat_payload,
        conversation_id=conversation_id,
        assistant_message_entity=assistant_message_entity,
        bot_name=bot_name,
        tools_message_entity=tools_message_entity,
    )

    if chat_payload.stream_id is not None and results["message"].get("content"):
        is_ar = is_arabic(results["message"]["content"][:30])
        asyncio.create_task(
            avatar_connector.render_text_async(chat_payload.stream_id, results["message"]["content"], is_ar)
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
        chat_history.append(msg)
    chat_history.append(chat_payload.messages[-1].model_dump())

    return {"system_message": system_message, "chat_history": chat_history}


def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)


