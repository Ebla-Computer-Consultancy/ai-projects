import asyncio
import json
import uuid
from wrapperfunction.website.model.chat_payload import ChatPayload
from wrapperfunction.website.model.chat_message import ChatMessage
from wrapperfunction.website.model.chat_message import Roles
from wrapperfunction.core import config
import wrapperfunction.integration as integration
from wrapperfunction.website.model.search_criterial import searchCriteria
from fastapi import status, HTTPException


def search(rs: searchCriteria):
    try:
    
        search_text = rs.query
 
        filter_expression = None
        if rs.facet:
            filter_expression = "metadata_author eq '{0}'".format(rs.facet)
        sort_expression = "search.score()"


        results = integration.aisearchconnector.search_query(
            config.SEARCH_INDEX,
            search_text,
            filter_expression,
            sort_expression,
            rs.page_size,
            rs.page_number,
        )

        return results

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


async def chat(chat_payload: ChatPayload):
    try:
        chat_history_arr = chat_payload.messages
        conversation_id = chat_payload.conversation_id or str(uuid.uuid4())

        if any(x.role == "system" for x in chat_history_arr):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "System messages are not allowed"
            )
        
        chat_history = []
        is_ar = is_arabic(chat_history_arr[-1].content)

        if chat_payload.stream_id:
            if is_ar:
                system_message = f"IMPORTANT: Represent numbers in alphabet only, not numeric. Always respond with very short answers. {config.SYSTEM_MESSAGE}"
            else:
                system_message = f"{config.SYSTEM_MESSAGE}, I want you to detect the input language and respond in the same language. Always respond with very short answers."
        else:
            system_message = f"{config.SYSTEM_MESSAGE}, I want you to detect the input language and respond in the same language."
        
        system_message += " If the user asks about a topic outside your knowledge, suggest relevant resources or someone knowledgeable instead of answering."
        chat_history.append({"role": Roles.System.value, "content": system_message})

        for item in chat_history_arr:
            chat_history.append(item.model_dump())

        results = integration.openaiconnector.chat_completion_mydata(
            config.SEARCH_INDEX, chat_history, system_message
        )

        if chat_payload.stream_id is not None:
            is_ar = is_arabic(results["message"]["content"][:30])
            asyncio.create_task(
                integration.avatarconnector.render_text_async(
                    chat_payload.stream_id, results["message"]["content"], is_ar
                )
            )

        if not chat_payload.conversation_id:
            integration.chatconnector.start_new_chat(chat_payload.user_id, conversation_id,results["message"]["content"],Roles.User.value)
            integration.chatconnector.add_to_chat_history(chat_payload.user_id, results["message"]["content"], conversation_id, Roles.User.value)
        else:
            integration.chatconnector.add_to_chat_history(chat_payload.user_id, results["message"]["content"], conversation_id, Roles.User.value)

        return {"conversation_id": conversation_id, "results": results}

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)

