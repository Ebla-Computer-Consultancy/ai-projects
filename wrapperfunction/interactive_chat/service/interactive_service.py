
from fastapi import HTTPException
from wrapperfunction.chat_history.model.message_entity import MessageEntity
from wrapperfunction.chatbot.integration.openai_connector import chat_completion
from wrapperfunction.chatbot.model.chat_message import ChatMessage
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.service.chatbot_service import add_all_messages_to_Entity, add_message_to_Entity
from wrapperfunction.core.config import ENTITY_SETTINGS
from wrapperfunction.core.model.entity_setting import ChatbotSetting, CustomSettings
from wrapperfunction.interactive_chat.model.interactive_model import GetForm, Status
from wrapperfunction.interactive_chat.service import functions
from wrapperfunction.chatbot.model.chat_message import Roles


async def submit_form(arguments:dict, chat_payload: ChatPayload):
    try:
        print(f"TYPE:{arguments.form}")
        print(f"Values:{arguments.form}")
        
        functions.fill_form(arguments.form)
        final_message = await generate_final_resopnse("form filled successfuly", chat_payload.conversation_id)
        return{
            "isComplete":True,
            "response": final_message
        }
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def approve_action(arguments:Status, chat_payload: ChatPayload):
    try:
        result = functions.approve_vacation(arguments.employee_name, arguments.employee_department)
        final_message = generate_final_resopnse(result, chat_payload.conversation_id)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def disapprove_action(arguments:Status, chat_payload: ChatPayload):
    try:
        
        result = functions.disapprove_vacation(arguments.employee_name, arguments.employee_department)
        final_message = generate_final_resopnse(result, chat_payload.conversation_id)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def pending_action(arguments:Status, chat_payload: ChatPayload):
    try:
        result = functions.pending_vacation(arguments.employee_name, arguments.employee_department)
        final_message = generate_final_resopnse(result, chat_payload.conversation_id)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def getForm_action(arguments: GetForm, chat_payload: ChatPayload):
    try:
        print(f'Argument-Type:{type(arguments)}')
        print(f'Argument:{arguments}')
        
        result = functions.get_forms(arguments.coulomn_name,arguments.value)
        final_message = await generate_final_resopnse(result, chat_payload.conversation_id)
        return {
            "isComplete":True,
            "response": str(result),
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def getAllForms_action(chat_payload: ChatPayload):
    try:
        result = functions.get_all_forms()
        final_message = await generate_final_resopnse(result, chat_payload.conversation_id)
        return {
            "isComplete":True,
            "response": str(result),
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
        
async def generate_final_resopnse(result, chat_payload: ChatPayload):
    msg = f'''"Generate a good response using the user's language and suggest for user a next step."
     f"Here are the results: {result}."
     {ENTITY_SETTINGS.get("suggestion_message")}
    '''

    final_response = chat_completion(
                            chatbot_setting=ChatbotSetting(
                                system_message=msg,
                                custom_settings=CustomSettings(
                                    max_tokens=4000,
                                    temperature=0.95
                                    )
                                ),
                            chat_history=[{"user":msg}],
                        )
    user_message_entity = MessageEntity(
        role=Roles.User.value,
        content=msg,
        conversation_id=chat_payload.conversation_id)
    
    assistant_message_entity = MessageEntity(
        role=Roles.Assistant.value,
        content=final_response.choices[0].message.content,
        conversation_id=chat_payload.conversation_id)
                  
    add_all_messages_to_Entity(
        chat_payload=chat_payload,
        conversation_id=chat_payload.conversation_id,
        user_message_entity=user_message_entity,
        assistant_message_entity=assistant_message_entity,
        bot_name="interactive")
    
    return final_response.choices[0].message.content
