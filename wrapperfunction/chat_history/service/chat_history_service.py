import asyncio
import json
from typing import Optional
import uuid
from wrapperfunction.chatbot.integration.openai_connector import chat_completion
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.core import config
from fastapi import HTTPException, Request
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
from wrapperfunction.core.utls.helper import extract_client_details
from wrapperfunction.document_intelligence.integration.document_intelligence_connector import analyze_file
from wrapperfunction.video_indexer.service import vi_service





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
    
def get_message_data(message_id):
    try:
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f" {MessagePropertyName.MESSAGE_ID.value} eq '{message_id}'")     
        return res[0]
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))    

def get_messages(conversation_id: Optional[str] = None, filter_condition: Optional[str] = None):
    try:
        if conversation_id:
            conversation_filter = f"{MessagePropertyName.CONVERSATION_ID.value} eq '{conversation_id}'"
            final_filter = f"{conversation_filter} and {filter_condition}" if filter_condition else conversation_filter
        else:
            final_filter = filter_condition
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME, final_filter) if final_filter else db_connector.get_entities(config.MESSAGE_TABLE_NAME)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
        


def get_user_messages(conversation_id):
    try:
        res=db_connector.get_entities(config.MESSAGE_TABLE_NAME,f"{MessagePropertyName.CONVERSATION_ID.value} eq '{conversation_id}' and {MessagePropertyName.ROLE.value} eq '{Roles.User.value}' and {MessagePropertyName.MessageType.value} eq '{MessageType.Message.value}'") 
        return list(res)

    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
def get_conversations_by_bot_name(bot_name: Optional[str] = None):
    try:
        filter_condition = f"{ConversationPropertyName.BOT_NAME.value} eq '{bot_name}'" if bot_name else None
        res = db_connector.get_entities(config.CONVERSATION_TABLE_NAME, filter_condition)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail="An error occurred while fetching conversations.")

def get_conversations_by_condition(condition: str):
    try:        
        res = db_connector.get_entities(config.CONVERSATION_TABLE_NAME, condition)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail="An error occurred while fetching conversations.")
    
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
def update_message(updated_data: dict,message_ids: list[str]):
    try:
        for message_id in message_ids:
            message = get_message_data(message_id)
            if message:
                message.update(updated_data)
                db_connector.update_entity(config.MESSAGE_TABLE_NAME, message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    
def perform_sentiment_analysis():
    try:
        excluded_chatbots = [chatbot["name"] for chatbot in config.ENTITY_SETTINGS.get("chatbots", []) if not chatbot.get("apply_sentiment", True)]
        conversations = get_conversations_by_condition(
            condition=f"{ConversationPropertyName.SENTIMENT.value} eq 'undefined'"
        )
        for conversation in conversations:
            conversation_id = conversation[ConversationPropertyName.CONVERSATION_ID.value]
            bot_name = conversation[ConversationPropertyName.BOT_NAME.value]
            
            if not conversation_id or bot_name in excluded_chatbots:
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

    
def perform_feedback_update(feedback: int,conversation_id:str):
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

async def add_message(chat_payload: ChatPayload, bot_name: str, request: Request):
    try:
        conv_id = chat_payload.conversation_id or str(uuid.uuid4())
        user_id = chat_payload.user_id or str(uuid.uuid4())
        if not chat_payload.conversation_id:
            title = chat_payload.messages[0].content[:20].strip()
            client_details = extract_client_details(request)
            message_entity = MessageEntity(chat_payload.messages[0].content, conv_id, Roles.User.value, "")
            conv_entity = ConversationEntity(user_id, conv_id, bot_name, title,client_ip=client_details["client_ip"],forwarded_ip=client_details["forwarded_ip"],device_info=json.dumps(client_details["device_info"]))
            await add_entity(message_entity, None, conv_entity)  
        else:
            message_entity = MessageEntity(chat_payload.messages[0].content, conv_id, Roles.User.value, "")
            await add_entity(message_entity)  
        return ServiceReturn(
            status=StatusCode.SUCCESS, message="message added successfully", data=conv_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
async def upload_documents(files, bot_name,  request: Request,conversation_id: Optional[str] = None ):
    try:
        content = ""
        for file in files:
            extracted_text = analyze_file(file, model_id='prebuilt-read').content
            content += extracted_text
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            title = content[:20].strip()
            user_message_entity = MessageEntity(content=content, conversation_id=conversation_id, role=Roles.User.value, context="", type=MessageType.Document.value)
            client_details = extract_client_details(request)
            conv_entity = ConversationEntity(user_id=str(uuid.uuid4()), conversation_id=conversation_id, bot_name=bot_name, title=title,client_ip=client_details["client_ip"],forwarded_ip=client_details["forwarded_ip"],device_info=json.dumps(client_details["device_info"]))
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

def set_message(conversation_id, role,message_id, content=None, tool_calls=None, context=None, completion_tokens=None, prompt_tokens=None, total_tokens=None, question_id=None, exception=None):
    if role is not Roles.Tool.value:
        return MessageEntity(
            conversation_id=conversation_id,
            content=content,
            role=role,
            context=context,
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
            question_id=question_id,
            message_id=message_id,
            exception=exception
        )
    return [
        MessageEntity(
            conversation_id=conversation_id,
            content=json.dumps(tool_call, ensure_ascii=False),
            role=Roles.Tool.value,
            context=context,
            message_id=message_id,
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
            question_id=question_id,
            exception=exception
        )
        for tool_call in tool_calls
    ]

async def add_messages_to_history(
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
        await handle_tool_messages(chat_payload, conversation_id, user_message_entity, tools_message_entity)
    else:
        await handle_user_or_assistant_messages(
            chat_payload, conversation_id, bot_name, user_message_entity, assistant_message_entity, client_ip, forwarded_ip, device_info
        )

def save_history(
    role, chat_payload, conversation_id,message_id, bot_name ,question_id=None,client_details=None, chat_history_with_system=None, results=None,exception=None
):
    if role == Roles.User.value:
        user_message_entity = set_message(
            conversation_id=conversation_id,
            content=chat_history_with_system["chat_history"][-1]["content"],
            role=Roles.User.value,
            message_id=message_id,
            exception=exception
        )

        asyncio.create_task(add_messages_to_history(
            chat_payload=chat_payload,
            conversation_id=conversation_id,
            bot_name=bot_name,
            user_message_entity=user_message_entity,
            client_ip=client_details["client_ip"],
            forwarded_ip=client_details["forwarded_ip"],
            device_info=json.dumps(client_details["device_info"]),
        ))

    elif role in [Roles.Assistant.value, Roles.Tool.value]:
        context = set_context(results)
        tools_message_entity = None
        assistant_message_entity = None

        if results["message"].get("tool_calls"):
            tools_message_entity = set_message(
                conversation_id=conversation_id,
                role=Roles.Tool.value,
                tool_calls=results["message"]["tool_calls"],
                context=context,
                completion_tokens=results["usage"]["completion_tokens"],
                prompt_tokens=results["usage"]["prompt_tokens"],
                total_tokens=results["usage"]["total_tokens"],
                question_id=question_id,
                message_id=message_id,
                exception=exception
            )
        else:
            assistant_message_entity = set_message(
                conversation_id=conversation_id,
                content=results["message"]["content"],
                role=Roles.Assistant.value,
                context=context,
                completion_tokens=results["usage"]["completion_tokens"],
                prompt_tokens=results["usage"]["prompt_tokens"],
                total_tokens=results["usage"]["total_tokens"],
                question_id=question_id,
                message_id=message_id,
                exception=exception
            )

        asyncio.create_task(add_messages_to_history(
            chat_payload=chat_payload,
            conversation_id=conversation_id,
            assistant_message_entity=assistant_message_entity,
            bot_name=bot_name,
            tools_message_entity=tools_message_entity,
        ))

async def create_and_add_message(chat_payload, conversation_id, user_message_entity, bot_name=None, client_ip=None, forwarded_ip=None, device_info=None):

    conv_entity = set_conversation_entity(
        chat_payload, conversation_id, user_message_entity, bot_name, client_ip, forwarded_ip, device_info
    )
    await add_message_to_Entity(user_message_entity=user_message_entity, conv_entity=conv_entity)

async def handle_tool_messages(
    chat_payload, 
    conversation_id, 
    user_message_entity, 
    tools_message_entity
):
    if not chat_payload.conversation_id and user_message_entity:
         await create_and_add_message(chat_payload, conversation_id, user_message_entity)
    else:
        for tool_message in tools_message_entity:
            await add_message_to_Entity(user_message_entity=user_message_entity, assistant_message_entity=tool_message)

async def handle_user_or_assistant_messages(
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
       await create_and_add_message(
            chat_payload, 
            conversation_id, 
            user_message_entity, 
            bot_name, 
            client_ip, 
            forwarded_ip, 
            device_info
        )
    else:
       await add_message_to_Entity(user_message_entity=user_message_entity, assistant_message_entity=assistant_message_entity)

def set_conversation_entity(chat_payload, conversation_id, user_message_entity, bot_name=None, client_ip=None, forwarded_ip=None, device_info=None):
    
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

async def add_message_to_Entity(user_message_entity=None, assistant_message_entity=None, conv_entity=None):
    if conv_entity and user_message_entity:
       await add_entity(message_entity=user_message_entity, conv_entity=conv_entity)
    else:
       await add_entity(
             message_entity=user_message_entity, assistant_entity=assistant_message_entity
        )




def get_question_answer_pairs():
    try:
        messages = get_messages(filter_condition=f"{MessagePropertyName.IS_ANSWERED.value} eq 'undefined'")
        if isinstance(messages, HTTPException):
            return messages.detail
        
        messages = sorted(messages, key=lambda x: (x["timestamp"], x["conversation_id"]))
        questions = {msg["message_id"]: msg for msg in messages if msg["role"] == Roles.User.value and "question_id" not in msg}
        qna_pairs = []
        
        for message in messages:
            if message["role"] == Roles.Assistant.value and "question_id" in message:
                question = questions.get(message["question_id"])
                if question:
                    qna_pairs.append({"question": question, "answer": message})
        
        return qna_pairs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Q&A pairs: {str(e)}")
def CheckQuestionAnswered(question: str, answer: str) -> bool:
    try:
        chatbot_settings = config.load_chatbot_settings("check_answered")
        chatbot_settings.system_message = (
    "You are a helpful assistant. "
    "Your task is to determine if the provided answer adequately addresses the question. "
    "Reply with 'True' if the answer is correct, otherwise reply with 'False'."
)

        prompt = [
    {"role": "system", "content": chatbot_settings.system_message},
    {"role": "user", "content": f"Question: {question}\nAnswer: {answer}\nDoes the answer correctly address the question? Reply with 'True' or 'False' only."}
]
        result = chat_completion(chatbot_settings, prompt)
        response_content = result["message"]["content"].strip()

        return response_content == "True"
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating question and answer: {str(e)}")




async def log_error_to_db(
    error_message: str,
    stack_trace: str,
    conversation_id: str,
    question_id: str
):
    try:
        full_exception_details = f"{error_message}\nStackTrace:\n{stack_trace}"

        error_entity = MessageEntity(
            content="An error occurred.",
            conversation_id=conversation_id,
            role=Roles.Assistant.value,
            context="Error Logging",
            message_id=str(uuid.uuid4()),
            exception=full_exception_details,
            question_id=question_id
        )

        await db_connector.add_entity(config.MESSAGE_TABLE_NAME, error_entity.to_dict())

        return ServiceReturn(status=StatusCode.SUCCESS, message="Error logged successfully").to_dict()

    except Exception as e:
        return ServiceReturn(status=StatusCode.INTERNAL_SERVER_ERROR, message=f"Failed to log error: {str(e)}").to_dict()
     
async def start_video_chat(video_id: str, request: Request, bot_name: str):
    try:
        response = await vi_service.get_video_index(video_id=video_id, bot_name=bot_name)
        res_data = response.get("data", {})
        client_details = extract_client_details(request)
        conversation_id = str(uuid.uuid4())
        conv_entity = ConversationEntity(
            user_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            bot_name=bot_name,
            title=res_data.get("name", ""),
            client_ip=client_details["client_ip"],
            forwarded_ip=client_details["forwarded_ip"],
            device_info=json.dumps(client_details["device_info"]),
        )

        message_entity = MessageEntity(
            content=json.dumps(res_data),
            conversation_id=conversation_id,
            message_id=str(uuid.uuid4()),
            role=Roles.User.value,
            context="",
            type=MessageType.Video.value,
        )

        await add_entity(message_entity=message_entity, conv_entity=conv_entity)

        return ServiceReturn(
            status=StatusCode.SUCCESS,
            message="Video chat started successfully",
            data=conversation_id,
        ).to_dict()
    except Exception as e:
        return ServiceReturn(
            status=StatusCode.INTERNAL_SERVER_ERROR,
            message=f"Error occurred: {str(e)}",
        ).to_dict()