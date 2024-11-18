from fastapi import APIRouter
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.interactive_chat.model.interactive_model import GetForm, Prompt, Status, SubmitForm
from wrapperfunction.interactive_chat.service import interactive_service

router = APIRouter()

@router.post("/chat/submit")
async def submit_form(request: SubmitForm, chat_payload: ChatPayload):
    return await interactive_service.submit_form(request.form,chat_payload)

@router.post("/chat/approve")
async def approve_action(arguments:Status, chat_payload: ChatPayload):
    return await interactive_service.approve_action(arguments,chat_payload)

@router.post("/chat/disapprove")
async def disapprove_action(arguments:Status, chat_payload: ChatPayload):
    return await interactive_service.disapprove_action(arguments,chat_payload)

@router.post("/chat/pending")
async def pending_action(arguments:Status, chat_payload: ChatPayload):
    return await interactive_service.pending_action(arguments,chat_payload)

@router.get("/chat/filter_vacation_forms_by")
async def getForm_action(arguments: GetForm, chat_payload: ChatPayload):
    return await interactive_service.getForm_action(arguments,chat_payload)
    
@router.get("/chat/get_all_vacation_forms")
async def getAllForms_action(chat_payload: ChatPayload):
    return await interactive_service.getAllForms_action(chat_payload) 
