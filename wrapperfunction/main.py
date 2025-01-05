# Fast Api
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from wrapperfunction.function_auth.ctrl import func_auth_ctrl
from wrapperfunction.function_auth.service.jwt_service import decode_jwt
from wrapperfunction.interactive_chat.ctrl import interactive_ctrl
from wrapperfunction.speech.ctrl import speech_ctrl
from wrapperfunction.chatbot.ctrl import chatbot_ctrl
from wrapperfunction.avatar.ctrl import avatar_ctrl
from wrapperfunction.admin.ctrl import admin_ctrl
from wrapperfunction.search.ctrl import search_ctrl
from wrapperfunction.document_intelligence.ctrl import document_intelligence_ctrl
from wrapperfunction.chat_history.ctrl import chat_history_ctrl
from wrapperfunction.media_monitoring.ctrl import media_ctrl

# app = FastAPI(dependencies=[Depends(test_ldap_connection)])
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "https://github.com/Ebla-Computer-Consultancy",
    #     "http://localhost",
    #     "http://localhost:7071",
    # ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(func_auth_ctrl.router, prefix="/api/v1/user", tags=["user"])
app.include_router(search_ctrl.router, prefix="/api/v1/search", tags=["search"], dependencies=[Depends(decode_jwt)])
app.include_router(chatbot_ctrl.router, prefix="/api/v1/chatbot", tags=["chatbot"], dependencies=[Depends(decode_jwt)])
app.include_router(interactive_ctrl.router, prefix="/api/v1/interactive", tags=["chatbot"], dependencies=[Depends(decode_jwt)])
app.include_router(avatar_ctrl.router, prefix="/api/v1/avatar", tags=["avatar"], dependencies=[Depends(decode_jwt)])
app.include_router(speech_ctrl.router, prefix="/api/v1/speech", tags=["speech"], dependencies=[Depends(decode_jwt)])
app.include_router(admin_ctrl.router, prefix="/api/v1/admin", tags=["admin"], dependencies=[Depends(decode_jwt)])
app.include_router(document_intelligence_ctrl.router,prefix="/api/v1/document-intelligence",tags=["document-intelligence"], dependencies=[Depends(decode_jwt)])
app.include_router(chat_history_ctrl.router, prefix="/api/v1/chat-history", tags=["chat-history"], dependencies=[Depends(decode_jwt)])
app.include_router(media_ctrl.router, prefix="/api/v1/media", tags=["media"], dependencies=[Depends(decode_jwt)])
