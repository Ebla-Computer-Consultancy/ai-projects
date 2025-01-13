import azure.functions as func
from wrapperfunction.main import app as fastapi_app
# for blue_print
from blue_print_functions.http_trigger_blue_print import bp as http_trigger_blue_print
from blue_print_functions.blob_trigger_blue_print import bp as blob_trigger_blue_print

app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
# app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(http_trigger_blue_print)
app.register_functions(blob_trigger_blue_print)