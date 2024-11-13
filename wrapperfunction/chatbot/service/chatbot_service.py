import asyncio
import json
from wrapperfunction.chatbot.model.chat_payload import ChatPayload 
from wrapperfunction.chatbot.model.chat_message import  Roles
from wrapperfunction.core import config
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.chat_history.service.chat_history_service as cosmos_db_service
from wrapperfunction.chat_history.model.message_entity import MessageEntity
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity
import wrapperfunction.avatar.service.avatar_service as avatarservice
from fastapi import status, HTTPException
import uuid 

async def chat(bot_name: str, chat_payload: ChatPayload):
    try:
        chat_history_arr = chat_payload.messages
        conversation_id = chat_payload.conversation_id or str(uuid.uuid4())
        user_id = chat_payload.user_id or str(uuid.uuid4())


        if any(x.role == "system" for x in chat_history_arr):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "system messages are not allowed"
            )


        chat_history = []
        is_ar = is_arabic(chat_history_arr[-1].content)
        if chat_payload.stream_id:
            if is_ar:
                system_message = f"IMPORTANT: Represent numbers in alphabet only not numeric. Always respond with very short answers. {config.SYSTEM_MESSAGE}"
            else:
                system_message = f"{config.SYSTEM_MESSAGE}, I want you to detect the input language and responds in the same language. Always respond with very short answers."
        else:
            system_message = f"{config.SYSTEM_MESSAGE}, I want you to detect the input language and responds in the same language."

        system_message+=" If user asked you about a topic outside your knowledge, never answer but suggest relevant resources or someone knowledgeable."

        chat_history.insert(0, {"role": Roles.System.value, "content": system_message})
        for item in chat_history_arr:
            chat_history.append(item.model_dump())
        
  
        chatbot_settings = config.load_chatbot_settings(bot_name)

        # Get response from OpenAI ChatGPT
        results = openaiconnector.chat_completion_mydata(
            chatbot_settings, chat_history, system_message
        )
        user_message_entity = MessageEntity(conversation_id=conversation_id,content=chat_history_arr[-1].content,role=Roles.User.value,)
        assistant_message_entity = MessageEntity(conversation_id=conversation_id,content=results["message"]["content"], role=Roles.Assistant.value)
        conv_entity=ConversationEntity(user_id,conversation_id,bot_name)
        if chat_payload.stream_id:
            is_ar = is_arabic(results["message"]["content"][:30])
            # await integration.avatarconnector.render_text_async(chat_payload.stream_id,results['message']['content'])
            asyncio.create_task(
                avatarservice.render_text_async(
                    chat_payload.stream_id, results["message"]["content"], is_ar
                )
            )        
        if not chat_payload.conversation_id:
           asyncio.create_task(
              cosmos_db_service.add_entity(
                user_message_entity,assistant_message_entity,conv_entity
                ),
            )
        else:
         asyncio.create_task(
              cosmos_db_service.add_entity(user_message_entity,assistant_message_entity),
            )

        return {"conversation_id": conversation_id, "results": results}

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})

def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)
