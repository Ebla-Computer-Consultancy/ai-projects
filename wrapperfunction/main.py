# Fast Api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from wrapperfunction.speech.ctrl import speech_ctrl
from wrapperfunction.chatbot.ctrl import chatbot_ctrl
from wrapperfunction.avatar.ctrl import avatar_ctrl
from wrapperfunction.admin.ctrl import admin_ctrl
from wrapperfunction.search.ctrl import search_ctrl
from wrapperfunction.interactive_chat.ctrl import chat_ctrl

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

app.include_router(search_ctrl.router, prefix="/api/v1/search", tags=["search"])
app.include_router(chatbot_ctrl.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(avatar_ctrl.router, prefix="/api/v1/avatar", tags=["avatar"])
app.include_router(speech_ctrl.router, prefix="/api/v1/speech", tags=["speech"])
app.include_router(admin_ctrl.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(chat_ctrl.router, prefix="/api/v1/interactive_chat", tags=["chatbot"])
