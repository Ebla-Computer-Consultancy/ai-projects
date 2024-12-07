from fastapi import APIRouter, HTTPException
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.interactive_chat.model.interactive_model import DepartmentTypes, GetForm, Status, SubmitForm, VacationForm, VacationTypes
from wrapperfunction.interactive_chat.service.interactive_service import approve_action, disapprove_action, getAllForms_action, getForm_action, pending_action, submit_form

router = APIRouter()

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
async def submit_form_action(form: VacationForm, chat_payload: ChatPayload):
    try:
        return await submit_form(form,chat_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action/approve")
async def approve_form_action(arguments:Status, chat_payload: ChatPayload):
    try:
        return await approve_action(arguments,chat_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/reject")
async def disapprove_form_action(arguments:Status, chat_payload: ChatPayload):
    try:
        return await disapprove_action(arguments,chat_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/pending")
async def pending_form_action(arguments:Status, chat_payload: ChatPayload):
    try:
        return await pending_action(arguments,chat_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/filter-vacation-forms-by")
async def getForm_form_action(arguments: GetForm, chat_payload: ChatPayload):
    try:
        return await getForm_action(arguments,chat_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/action/get-all-vacation-forms")
async def get_All_Forms_action(chat_payload: ChatPayload):
    try:
        return await getAllForms_action(chat_payload) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))