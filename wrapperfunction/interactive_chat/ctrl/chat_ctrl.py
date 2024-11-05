from fastapi import APIRouter
from wrapperfunction.interactive_chat.model.interactive_chat_model import GetForm, Prompt, Status, SubmitForm
from wrapperfunction.interactive_chat.service import chat_service

router = APIRouter()

@router.post("/chat")
async def chat(request: Prompt):
    return await chat_service.active_chat(request.prompt)

#### ACTION ENDPOINTS ####
@router.post("/chat/submit")
async def submit_form(request: SubmitForm):
    return await chat_service.submit_form(request.form)

@router.post("/chat/approve")
async def approve_action(arguments:Status):
    return await chat_service.approve_action(arguments)

@router.post("/chat/disapprove")
async def disapprove_action(arguments:Status):
    return await chat_service.disapprove_action(arguments)

@router.post("/chat/pending")
async def pending_action(arguments:Status):
    return await chat_service.pending_action(arguments)

@router.get("/chat/filter_vacation_forms_by")
async def getForm_action(arguments: GetForm):
    return await chat_service.getForm_action(arguments)
    
@router.get("/chat/get_all_vacation_forms")
async def getAllForms_action():
    return await chat_service.getAllForms_action() 
