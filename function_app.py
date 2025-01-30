import azure.functions as func
from wrapperfunction.main import app as fastapi_app
from wrapperfunction.media_monitoring.blueprint.media_blueprint import media_bp
app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
# app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(media_bp)