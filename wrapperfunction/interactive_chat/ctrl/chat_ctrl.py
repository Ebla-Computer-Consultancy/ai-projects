from fastapi import APIRouter
from wrapperfunction.interactive_chat.model.interactive_chat_model import GetForm, Prompt, Status, SubmitForm
from wrapperfunction.interactive_chat.service import manager_service, user_service

router = APIRouter()

@router.post("/user_chat")
async def user_chat(request: Prompt):
    return await user_service.user_chat(request.prompt)

@router.post("/user_chat/submit_vacation_form")
async def user_submit_form(request: SubmitForm):
    return await user_service.user_submit_form(request.form)

@router.post("/manager_chat")
async def manager_chat(request: Prompt):
    return await manager_service.manager_chat(request.prompt)

@router.post("/manager_chat/approve_vacation")
async def manager_approve_action(arguments:Status):
    return await manager_service.manager_approve_action(arguments)

@router.post("/manager_chat/disapprove_vacation")
async def manager_disapprove_action(arguments:Status):
    return await manager_service.manager_disapprove_action(arguments)

@router.post("/manager_chat/pending_vacation")
async def manager_pending_action(arguments:Status):
    return await manager_service.manager_pending_action(arguments)

@router.get("/manager_chat/filter_vacation_forms_by")
async def manager_getForm_action(arguments: GetForm):
    return await manager_service.manager_getForm_action(arguments)
    
@router.get("/manager_chat/get_all_vacation_forms")
async def manager_getAllForms_action():
    return await manager_service.manager_getAllForms_action() 
