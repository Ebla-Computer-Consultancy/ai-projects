
import json
from fastapi import HTTPException
from wrapperfunction.chat_history.model.message_entity import MessageEntity
from wrapperfunction.chatbot.integration.openai_connector import chat_completion
from wrapperfunction.chatbot.model.chat_message import ChatMessage
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.service import chatbot_service
from wrapperfunction.core.config import ENTITY_SETTINGS
from wrapperfunction.core.model.entity_setting import ChatbotSetting, CustomSettings
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.interactive_chat.model import interactive_model
from wrapperfunction.interactive_chat.service import functions
from wrapperfunction.chatbot.model.chat_message import Roles


async def submit_form(arguments:dict, chat_payload: ChatPayload):
    try:
        print(f"TYPE:{arguments.form}")
        print(f"Values:{arguments.form}")
        
        functions.fill_form(arguments.form)
        final_message = await generate_final_resopnse("form filled successfuly", chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "final_message": final_message
                            },
                        message=f"Form Submited Successfuly, form data:{arguments.form}"
                        ).to_dict()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while submitting form: {str(e)}")

async def approve_action(arguments:interactive_model.Status, chat_payload: ChatPayload):
    try:
        result = functions.approve_vacation(arguments.employee_ID)
        final_message = await generate_final_resopnse(result, chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": str(result),
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Approved Successfuly"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Approving form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Approving form:{arguments.employee_ID}: {str(e)}")


async def disapprove_action(arguments:interactive_model.Status, chat_payload: ChatPayload):
    try:
  
        result = functions.disapprove_vacation(arguments.employee_ID)
        final_message = await generate_final_resopnse(result, chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": str(result),
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Disapproved Successfuly"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Dissapproving form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Dissapproving form:{arguments.employee_ID}: {str(e)}")

async def pending_action(arguments:interactive_model.Status, chat_payload: ChatPayload):
    try:
        result = functions.pending_vacation(arguments.employee_ID)
        final_message = await generate_final_resopnse(result, chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": str(result),
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Pended Successfuly"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Pending form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Pending form:{arguments.employee_ID}: {str(e)}")

async def getForm_action(arguments: interactive_model.GetForm, chat_payload: ChatPayload):
    try:
        print(f'Argument-Type:{type(arguments)}')
        print(f'Argument:{arguments}')
        
        result = functions.get_forms(arguments.coulomn_name,try_parse_int(arguments.value))
        if not isinstance(result, str): 
            result = get_forms(result=result)
        final_message = await generate_final_resopnse(result, chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": result,
                            "final_message": final_message
                            },
                        message=f"All {arguments.coulomn_name}:{arguments.value} Forms Returned Successfuly"
                        ).to_dict()
    except Exception as e:
        print(f"Error While getting forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While getting forms: {str(e)}")

async def getAllForms_action(chat_payload: ChatPayload):
    try:
        result = functions.get_all_forms()
        if not isinstance(result, str): 
            result = get_forms(result=result)
        final_message = await generate_final_resopnse(result, chat_payload)
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            data={
                                "action_results": result,
                                "final_message": final_message
                                },
                            message="All Forms Returned Successfuly"
                            ).to_dict()
    except Exception as e:
        print(f"Error While getting forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While getting forms: {str(e)}") 
        
async def generate_final_resopnse(result, chat_payload: ChatPayload):
    msg = f'''"Generate a good response using the user's language and suggest for user a next step."
     f"Here are the results: {result}."
     {ENTITY_SETTINGS.get("suggestion_message")}
    '''

    final_response = chat_completion(
                            chatbot_setting=ChatbotSetting(
                                index_name=None,
                                name=None,
                                system_message=ENTITY_SETTINGS.get("suggestion_message"),
                                custom_settings=CustomSettings(
                                    max_tokens=4000,
                                    temperature=0.95
                                    )
                                ),
                            chat_history=[{"role":Roles.User.value,"content":msg}],
                        )
    context = chatbot_service.set_context(final_response)
    user_message_entity = chatbot_service.set_message(
        role=Roles.User.value,
        content=msg,
        conversation_id=chat_payload.conversation_id,
        context=context
        )
    
    assistant_message_entity = chatbot_service.set_message(
        role=Roles.Assistant.value,
        content=final_response["message"]["content"],
        conversation_id=chat_payload.conversation_id,
        context=context)
                
    chatbot_service.add_messages_to_history(
        chat_payload=chat_payload,
        conversation_id=chat_payload.conversation_id,
        user_message_entity=user_message_entity,
        assistant_message_entity=assistant_message_entity,
        bot_name="interactive")
    
    return final_response

def get_forms(result: list):
    try:
        return [interactive_model.VacationForm(type=form["Type"],
                                employee_name=form["Employee Name"],
                                employee_ID=int(form["ID"]),
                                manager_name=form["Manager Name"],
                                employee_department=form["Department"],
                                start_date=form["Start-date"],
                                end_date=form["End-date"],
                                total_days=form["Total days"],
                                status=form["Status"],
                                comments=str(form["Comments"]))
                                for form in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error While setting forms: {str(e)}")

def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return value
