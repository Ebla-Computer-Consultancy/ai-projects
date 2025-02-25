from fastapi import HTTPException, Request
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.chatbot.service import chatbot_service
from wrapperfunction.core import config
from wrapperfunction.core.config import ENTITY_SETTINGS
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.function_auth.service import jwt_service
from wrapperfunction.interactive_chat.model import interactive_model
from wrapperfunction.chatbot.model.chat_message import ChatMessage, Roles
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector


async def submit_form(form: interactive_model.VacationForm, chat_payload: ChatPayload, request: Request):
    try:
        v_form = interactive_model.VacationFormEntity(vacation_type=form.vacation_type,
                                            employee_ID=form.employee_ID,
                                            employee_name=form.employee_name,
                                            employee_department=form.employee_department,
                                            manager_name=form.manager_name,
                                            start_date=form.start_date,
                                            end_date=form.end_date,
                                            comments=form.comments).to_dict()
        result = await add_form(v_form)
        if result is None:
            result = f"Form Submitted Successfully, form data:{v_form}"
        final_message = await generate_final_response("form filled Successfully", chat_payload, request)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results":result,
                            "final_message": final_message
                            },
                        message=f"Form Submitted Successfully, form data:{v_form}"
                        ).to_dict()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while submitting form: {str(e)}")

async def approve_action(arguments:interactive_model.Status, chat_payload: ChatPayload, request: Request):
    try:
        token = jwt_service.get_token(request)
        role = jwt_service.get_user_role(token)
        if role == interactive_model.RoleTypes.MANAGER.value:
            result = update_Status(arguments.employee_ID,interactive_model.FormStatus.APPROVED.value)
            if result is None:
                result = f"Employee With ID:{arguments.employee_ID} Form Approved Successfully"
        else:
            result = f"Employee With ID:{arguments.employee_ID} Can not Approve because he is not a manager"
        final_message = await generate_final_response(result, chat_payload, request)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": result,
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Approved Successfully"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Approving form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Approving form:{arguments.employee_ID}: {str(e)}")


async def disapprove_action(arguments:interactive_model.Status, chat_payload: ChatPayload, request: Request):
    try:
        token = jwt_service.get_token(request)
        role = jwt_service.get_user_role(token)
        if role == interactive_model.RoleTypes.MANAGER.value:
            result = update_Status(arguments.employee_ID,interactive_model.FormStatus.REJECTED.value)
            if result is None:
                result = f"Employee With ID:{arguments.employee_ID} Form Rejected Successfully"
        else:
            result = f"Employee With ID:{arguments.employee_ID} Can not Reject because he is not a manager"
        final_message = await generate_final_response(result, chat_payload, request)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": str(result),
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Rejected Successfully"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Rejecting form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Rejected form:{arguments.employee_ID}: {str(e)}")

async def pending_action(arguments:interactive_model.Status, chat_payload: ChatPayload, request: Request):
    try:
        token = jwt_service.get_token(request)
        role = jwt_service.get_user_role(token)
        if role == interactive_model.RoleTypes.MANAGER.value:
            result = update_Status(arguments.employee_ID,interactive_model.FormStatus.PENDING.value)
            if result is None:
                result = f"Employee With ID:{arguments.employee_ID} Form Pended Successfully"
        else:
            result = f"Employee With ID:{arguments.employee_ID} Can not Pend because he is not a manager"
        final_message = await generate_final_response(result, chat_payload, request)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": str(result),
                            "final_message": final_message
                            },
                        message=f"Employee With ID:{arguments.employee_ID} Form Pended Successfully"
                        ).to_dict()
    except Exception as e:
        print(f"Error While Pending form:{arguments.employee_ID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While Pending form:{arguments.employee_ID}: {str(e)}")

async def filtered_form_action(arguments: interactive_model.GetForm, chat_payload: ChatPayload, request: Request):
    try:
        token = jwt_service.get_token(request)
        user_data = jwt_service.decode_jwt(token, clear_payload=True)
        employee_id = user_data.get("employee_ID",None)
        role = user_data.get("role",None)
        result = "Employee can not filter as he is not authenticated"
        if role == interactive_model.RoleTypes.MANAGER.value:
            result = get_vacations_filter_by(arguments.column_name,arguments.value)
        elif role == interactive_model.RoleTypes.EMPLOYEE.value:
            if employee_id:
                result = get_employee_vacations_filter_by(arguments.column_name,arguments.value, employee_id) 
        if len(result) == 0: 
            result = f"No forms found for {arguments.column_name}:{arguments.value}"
        final_message = await generate_final_response(result, chat_payload, request)
        return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        data={
                            "action_results": result,
                            "final_message": final_message
                            },
                        message=f"All {arguments.column_name}:{arguments.value} Forms Returned Successfully"
                        ).to_dict()
    except Exception as e:
        print(f"Error While getting forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While getting forms: {str(e)}")

async def getAllForms_action(chat_payload: ChatPayload, request: Request):
    try:
        token = jwt_service.get_token(request)
        role = jwt_service.get_user_role(token)
        if role == interactive_model.RoleTypes.MANAGER.value:
            result = get_all_vacations()
        else:
            result = f"Can not get all vacations because user he is not a manager"
        
        if len(result) == 0: 
            result = f"No forms found"
        final_message = await generate_final_response(result, chat_payload, request)
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            data={
                                "action_results": result,
                                "final_message": final_message
                                },
                            message="All Forms Returned Successfully"
                            ).to_dict()
    except Exception as e:
        print(f"Error While getting forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While getting forms: {str(e)}") 

async def get_all_employee_vacations_count(arguments: interactive_model.Status, chat_payload: ChatPayload, request: Request):
    try:
        result = get_vacations_filter_by("Employee_ID",1234)
        if len(result) == 0: 
            result = f"No forms found"
        final_message = await generate_final_response(f'Total Vacations Forms count:{len(result)}', chat_payload, request)
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            data={
                                "action_results": len(result),
                                "final_message": final_message
                                },
                            message="All Forms Returned Successfully"
                            ).to_dict()
    except Exception as e:
        print(f"Error While getting forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While getting Employee forms count: {str(e)}")

async def get_all_employee_vacation_forms(arguments: interactive_model.Status, chat_payload: ChatPayload, request: Request):
    try:
        result = get_vacations_filter_by("Employee_ID",1234)
        if len(result) == 0: 
            result = f"No forms found"
        final_message = await generate_final_response(result, chat_payload, request)
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            data={
                                "action_results": result,
                                "final_message": final_message
                                },
                            message="All Forms Returned Successfully"
                            ).to_dict()
    except Exception as e:
        print(f"Error While getting forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While getting Employee forms count: {str(e)}")
    
async def generate_final_response(result, chat_payload: ChatPayload, request: Request):
    try:
        chat_payload.messages.append(
            ChatMessage(
                role=Roles.User.value,
                content=f"Here are the results: {result}. what are your suggestion now? sample of suggestion:{ENTITY_SETTINGS.get('suggestion_message')} note: answer me with the language i used to talk with it in the previous messages. important note: dont call any function for this message only. important note: dont return None, make sure to give me a suggestion or a description about the results"
                )
            )
        final_response = await chatbot_service.chat("interactive",chat_payload, request)
        
        return final_response
    except Exception as e:
        print(f"Error While generating final message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error While generating final message: {str(e)}")

def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return value

def get_all_vacations():
    try:
        res =  db_connector.get_entities(config.COSMOS_VACATION_TABLE)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def get_vacations_filter_by(column_name,value):
    try:
        res =  db_connector.get_entities(config.COSMOS_VACATION_TABLE,f"{column_name} eq {value}")
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
 
def get_employee_vacations_filter_by(column_name,value, employee_id):
    try:
        query = f"Employee_ID eq {employee_id}"
        if column_name != "Employee_ID":
            query += f" and {column_name} eq {value}"
        res =  db_connector.get_entities(config.COSMOS_VACATION_TABLE,query)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))   

def update_Status(employee_ID: str, status: int):
    try:
        forms = get_vacations_filter_by("Employee_ID",employee_ID)
        if forms:
            for form in forms:
                
                form.update({"Status":status,"Comments":f"{interactive_model.FormStatus(status).name} by Manager"})
                db_connector.update_entity(config.COSMOS_VACATION_TABLE, form)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def add_form(form: dict):
    try:
        await db_connector.add_entity(config.COSMOS_VACATION_TABLE,form)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))