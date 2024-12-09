from fastapi import HTTPException
from wrapperfunction.chat_history.service import chat_history_service as db
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.service import chatbot_service
from wrapperfunction.core.config import ENTITY_SETTINGS
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.interactive_chat.model import interactive_model
from wrapperfunction.chatbot.model.chat_message import ChatMessage, Roles


async def submit_form(form: interactive_model.VacationForm, chat_payload: ChatPayload):
    try:
        v_form = interactive_model.VacationFormEntity(vacation_type=form.vacation_type,
                                             employee_ID=form.employee_ID,
                                             employee_name=form.employee_name,
                                             employee_department=form.employee_department,
                                             manager_name=form.manager_name,
                                             start_date=form.start_date,
                                             end_date=form.end_date,
                                             
                                             comments=form.comments).to_dict()
        result = await db.add_form(v_form)
        if result is None:
            result = f"Form Submited Successfuly, form data:{v_form}"
        final_message = await generate_final_resopnse("form filled successfuly", chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results":result,
                            "final_message": final_message
                            },
                        message=f"Form Submited Successfuly, form data:{v_form}"
                        ).to_dict()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while submitting form: {str(e)}")

async def approve_action(arguments:interactive_model.Status, chat_payload: ChatPayload):
    try:
        result = db.update_Status(arguments.employee_ID,interactive_model.FormStatus.APPROVED.value)
        if result is None:
            result = f"Employee With ID:{arguments.employee_ID} Form Approved Successfuly"
        final_message = await generate_final_resopnse(result, chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": result,
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Approved Successfuly"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Approving form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Approving form:{arguments.employee_ID}: {str(e)}")


async def disapprove_action(arguments:interactive_model.Status, chat_payload: ChatPayload):
    try:
  
        result = db.update_Status(arguments.employee_ID,interactive_model.FormStatus.REJECTED.value)
        if result is None:
            result = f"Employee With ID:{arguments.employee_ID} Form Rejeted Successfuly"
        final_message = await generate_final_resopnse(result, chat_payload)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": str(result),
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Rejeted Successfuly"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Rejeting form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Rejeting form:{arguments.employee_ID}: {str(e)}")

async def pending_action(arguments:interactive_model.Status, chat_payload: ChatPayload):
    try:
        result = db.update_Status(arguments.employee_ID,interactive_model.FormStatus.PENDING.value)
        if result is None:
            result = f"Employee With ID:{arguments.employee_ID} Form Pended Successfuly"
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
        
        result = db.get_vactions_filter_by(arguments.coulomn_name,arguments.value)
        if len(result) == 0: 
            result = f"No forms found for {arguments.coulomn_name}:{arguments.value}"
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
        result = db.get_all_vactions()
        if len(result) == 0: 
            result = f"No forms found"
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
    try:
        chat_payload.messages.append(
            ChatMessage(
                role=Roles.User.value,
                content=f"Here are the results: {result}. what are you suggestion now? sample of suggestion:{ENTITY_SETTINGS.get('suggestion_message')} note: answer me with the language i used to talk with it in the previos messages. important note: dont call any function for this message only"
                )
            )
        final_response = await chatbot_service.chat("interactive",chat_payload)
        
        return final_response
    except Exception as e:
        print(f"Error While generating final message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While generating final message: {str(e)}")

def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return value
