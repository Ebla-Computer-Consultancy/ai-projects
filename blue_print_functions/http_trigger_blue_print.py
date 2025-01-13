import azure.functions as func
from fastapi import FastAPI

app = FastAPI()
bp = func.Blueprint.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
