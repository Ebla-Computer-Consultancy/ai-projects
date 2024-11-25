import asyncio
import json
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.model.chat_message import Roles
from wrapperfunction.core import config
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.avatar.integration.avatar_connector as avatarconnector
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

        context = set_context(results)

        # Set user message
        user_message_entity = set_message(
            conversation_id=conversation_id,
            content=chat_history_with_system_message["chat_history"][-1]["content"],
            role=Roles.User.value,
            context=context,
        )
        # Set assistant or Tool message
        tools_message_entity = None
        assistant_message_entity = None
        if results["message"]["tool_calls"]:
            tools_message_entity = set_message(
                conversation_id=conversation_id,
                role=Roles.Tool.value,
                tool_calls=results["message"]["tool_calls"],
                context=context,
            )
        else:
            assistant_message_entity = set_message(
                conversation_id=conversation_id,
                content=results["message"]["content"],
                role=Roles.Assistant.value,
                context=context,
            )

        # Add Messages
        add_messages_to_history(
            chat_payload=chat_payload,
            conversation_id=conversation_id,
            user_message_entity=user_message_entity,
            assistant_message_entity=assistant_message_entity,
            bot_name=bot_name,
            tools_message_entity=tools_message_entity,
        )

        if chat_payload.stream_id is not None:
            is_ar = is_arabic(results["message"]["content"][:30])
            # await avatar connector.render_text_async(chat_payload.stream_id,results['message']['content'], is_ar)

            asyncio.create_task(
                avatarconnector.render_text_async(
                    chat_payload.stream_id, results["message"]["content"], is_ar
                )
            )

        results["message"]["conversation_id"] = conversation_id
        return results

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


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


def set_message(conversation_id, role, content=None, tool_calls=None, context=None):
    # Set message Entity
    if role is not Roles.Tool.value:
        return MessageEntity(
            conversation_id=conversation_id, content=content, role=role, context=context
        )
    return [
        MessageEntity(
            conversation_id=conversation_id,
            content=json.dumps(tool_call),
            role=Roles.Tool.value,
            context=context,
        )
        for tool_call in tool_calls
    ]


def add_messages_to_history(
    chat_payload,
    conversation_id,
    user_message_entity,
    bot_name,
    assistant_message_entity=None,
    tools_message_entity=None,
):
    user_id = chat_payload.user_id or str(uuid.uuid4())
    # Set Conversation Entity
    title = user_message_entity.content[:20].strip()
    conv_entity = ConversationEntity(user_id, conversation_id, bot_name, title=title)

    if not tools_message_entity:
        if not chat_payload.conversation_id:
            add_message_to_Entity(
                user_message_entity=user_message_entity,
                assistant_message_entity=assistant_message_entity,
                conv_entity=conv_entity,
            )
        else:
            add_message_to_Entity(
                user_message_entity=user_message_entity,
                assistant_message_entity=assistant_message_entity,
                conv_entity=None,
            )

    else:
        for tool_message in tools_message_entity:
            if not chat_payload.conversation_id:
                add_message_to_Entity(
                    user_message_entity=user_message_entity,
                    assistant_message_entity=tool_message,
                    conv_entity=conv_entity,
                )
            else:
                add_message_to_Entity(
                    user_message_entity=user_message_entity,
                    assistant_message_entity=tool_message,
                )


def add_message_to_Entity(
    user_message_entity, assistant_message_entity, conv_entity=None
):
    if conv_entity is not None:
        asyncio.create_task(
            chat_history_service.add_entity(
                user_message_entity, assistant_message_entity, conv_entity
            ),
        )
    else:
        asyncio.create_task(
            chat_history_service.add_entity(
                user_message_entity, assistant_message_entity
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
        return (
            "".join(results["message"]["content"].replace("\n", "").split()).strip(),
        )
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


def prepare_chat_history_with_system_message(chat_payload, bot_name):
    chat_history_arr = []
    if chat_payload.conversation_id:
        chat_history_arr = chat_history_service.get_messages(
            conversation_id=chat_payload.conversation_id
        )
    chat_history = []
    is_ar = is_arabic(chat_payload.messages[-1].content)
    if chat_payload.stream_id:
        if is_ar:
            system_message = f"IMPORTANT: Represent numbers in alphabet only not numeric. Always respond with very short answers. {config.load_chatbot_settings(bot_name).system_message}"
        else:
            system_message = f"{config.load_chatbot_settings(bot_name).system_message}, I want you to detect the input language and responds in the same language. Always respond with very short answers."
    else:
        system_message = f"{config.load_chatbot_settings(bot_name).system_message}, I want you to detect the input language and responds in the same language."
    system_message += " If user asked you about a topic outside your knowledge, never answer but suggest relevant resources or someone knowledgeable."
    chat_history.insert(0, {"role": Roles.System.value, "content": system_message})

    chat_history.extend(config.load_chatbot_settings(bot_name).examples)
    ##if have tools
    for item in chat_history_arr:
        msg = {"role": item["role"], "content": item["content"]}
        if (
            config.load_chatbot_settings(bot_name).custom_settings.tools
            and item["role"] == "tool"
        ):
            tool = json.loads(item["content"])
            tool["id"] = chat_payload.conversation_id
            tool["function"]["arguments"] = json.dumps(tool["function"]["arguments"])
            chat_history.append({"role": "assistant", "tool_calls": [tool]})
            msg["tool_call_id"] = chat_payload.conversation_id
        chat_history.append(msg)
    chat_history.append(chat_payload.messages[-1].model_dump())
    chat_history = chat_history[:1] + chat_history[-10:]

    return {"system_message": system_message, "chat_history": chat_history}


def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)
