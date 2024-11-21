from fastapi import APIRouter
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.interactive_chat.model.interactive_model import GetForm, Status, SubmitForm
from wrapperfunction.interactive_chat.service.interactive_service import approve_action, disapprove_action, getAllForms_action, getForm_action, pending_action, submit_form

router = APIRouter()

@router.post("/action/submit")
async def submit_form_action(request: SubmitForm, chat_payload: ChatPayload):
    return await submit_form(request.form,chat_payload)

@router.post("/action/approve")
async def approve_form_action(arguments:Status, chat_payload: ChatPayload):
    return await approve_action(arguments,chat_payload)

@router.post("/action/disapprove")
async def disapprove_form_action(arguments:Status, chat_payload: ChatPayload):
    return await disapprove_action(arguments,chat_payload)

@router.post("/action/pending")
async def pending_form_action(arguments:Status, chat_payload: ChatPayload):
    return await pending_action(arguments,chat_payload)

@router.get("/action/filter_vacation_forms_by")
async def getForm_form_action(arguments: GetForm, chat_payload: ChatPayload):
    return await getForm_action(arguments,chat_payload)
    
@router.get("/action/get_all_vacation_forms")
async def get_All_Forms_action(chat_payload: ChatPayload):
    return await getAllForms_action(chat_payload) 
