# Fast Api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from wrapperfunction.website.ctrl import ws_ctrl
from wrapperfunction.common.ctrl import common_ctrl
from wrapperfunction.admin.ctrl import admin_ctrl

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

app.include_router(ws_ctrl.router, prefix="/api/v1/website", tags=["website"])
app.include_router(common_ctrl.router, prefix="/api/v1/common", tags=["common"])
app.include_router(admin_ctrl.router, prefix="/api/v1/admin", tags=["admin"])
