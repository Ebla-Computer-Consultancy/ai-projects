from fastapi import APIRouter, HTTPException, Request
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.interactive_chat.model.interactive_model import DepartmentTypes, GetForm, RoleTypes, Status, VacationForm, VacationTypes
from wrapperfunction.interactive_chat.service.interactive_service import approve_action, disapprove_action, get_all_employee_vacation_forms, get_all_employee_vacations_count, getAllForms_action, filtered_form_action, pending_action, submit_form

router = APIRouter()

@router.get("/role-types")
async def get_role_types():
    try:
        return RoleTypes.to_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/department-types")
async def get_department_types():
    try:
        return DepartmentTypes.to_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/vacation-types")
async def get_vacation_types():
    try:
        return VacationTypes.to_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action/submit-form")
async def submit_form_action(form: VacationForm, chat_payload: ChatPayload, request: Request):
    try:
        return await submit_form(form,chat_payload,request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action/approve")
async def approve_form_action(arguments:Status, chat_payload: ChatPayload, request: Request):
    try:
        return await approve_action(arguments,chat_payload,request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/reject")
async def disapprove_form_action(arguments:Status, chat_payload: ChatPayload, request: Request):
    try:
        return await disapprove_action(arguments,chat_payload,request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/pending")
async def pending_form_action(arguments:Status, chat_payload: ChatPayload, request: Request):
    try:
        return await pending_action(arguments,chat_payload,request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/filter-vacation-forms-by")
async def get_filtered_form_action(arguments: GetForm, chat_payload: ChatPayload, request: Request):
    try:
        return await filtered_form_action(arguments,chat_payload,request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/get-all-vacation-forms")
async def get_All_Forms_action(chat_payload: ChatPayload, request: Request):
    try:
        return await getAllForms_action(chat_payload,request) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action/get-employee-vacations-count")
async def get_all_employee_forms_count(arguments:Status, chat_payload: ChatPayload, request: Request):
    try:
        return await get_all_employee_vacations_count(arguments,chat_payload,request) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action/get-employee-vacation-forms")
async def get_all_employee_forms(arguments:Status, chat_payload: ChatPayload, request: Request):
    try:
        return await get_all_employee_vacation_forms(arguments,chat_payload,request) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))