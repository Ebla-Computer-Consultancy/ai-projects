# Fast Api
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from wrapperfunction.FAQ.ctrl import FAQ_ctrl
from wrapperfunction.function_auth.ctrl import func_auth_ctrl
from wrapperfunction.function_auth.model.permission_enum import PermissionTypes
from wrapperfunction.interactive_chat.ctrl import interactive_ctrl
from wrapperfunction.social_media.ctrl import x_ctrl
from wrapperfunction.speech.ctrl import speech_ctrl
from wrapperfunction.chatbot.ctrl import chatbot_ctrl
from wrapperfunction.avatar.ctrl import avatar_ctrl
from wrapperfunction.admin.ctrl import admin_ctrl
from wrapperfunction.search.ctrl import search_ctrl
from wrapperfunction.document_intelligence.ctrl import document_intelligence_ctrl
from wrapperfunction.chat_history.ctrl import chat_history_ctrl
from wrapperfunction.media_monitoring.ctrl import media_ctrl
from wrapperfunction.video_indexer.ctrl import vi_ctrl
from wrapperfunction.chat_history.ctrl import localiazation_ctrl

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
app.include_router(search_ctrl.router, prefix="/api/v1/search", tags=["search"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.SEARCH.value))])
app.include_router(chatbot_ctrl.router, prefix="/api/v1/chatbot", tags=["chatbot"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.CHATBOT.value))])
app.include_router(interactive_ctrl.router, prefix="/api/v1/interactive", tags=["chatbot"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.INTERACTIVE_CHAT.value))])
app.include_router(avatar_ctrl.router, prefix="/api/v1/avatar", tags=["avatar"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.AVATAR.value))])
app.include_router(speech_ctrl.router, prefix="/api/v1/speech", tags=["speech"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.SPEECH.value))])
app.include_router(admin_ctrl.router, prefix="/api/v1/admin", tags=["admin"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.ADMIN.value))])
app.include_router(document_intelligence_ctrl.router,prefix="/api/v1/document-intelligence",tags=["document-intelligence"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.DOCUMENT_INTELLIGENCE.value))])
app.include_router(chat_history_ctrl.router, prefix="/api/v1/chat-history", tags=["chat-history"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.CHAT_HISTORY.value))])
app.include_router(media_ctrl.router, prefix="/api/v1/media", tags=["media"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.MEDIA.value))])
app.include_router(localiazation_ctrl.router,prefix="/api/v1/localization", tags=["Localization"])
app.include_router(x_ctrl.router, prefix="/api/v1/social", tags=["social"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.SOCIAL_MEDIA.value))])
app.include_router(vi_ctrl.router, prefix="/api/v1/vi", tags=["video-indexer"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.VIDEO_INDEXER.value))])
app.include_router(FAQ_ctrl.router, prefix="/api/v1/FAQ", tags=["FAQ"], dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.FAQ.value))])
app.include_router(localiazation_ctrl.router,prefix="/api/v1/localization", tags=["Localization"],dependencies=[Depends(func_auth_ctrl.hasAuthority(PermissionTypes.LOCALIZATION.value))])

