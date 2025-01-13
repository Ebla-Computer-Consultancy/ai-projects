import logging
import azure.functions as func
import pandas as pd
from io import BytesIO

from wrapperfunction.core.config import BLOB_CONTAINER_NAME

bp = func.Blueprint()


# first decorator sets the function name
@bp.function_name("blob_triggered")
# second decorator defines the trigger
@bp.blob_trigger(
    arg_name="obj",
    path=f"links",
    connection=BLOB_CONTAINER_NAME,
)
def custom_blob_trigger_function(obj: func.InputStream):
    logging.info("Python blob trigger function processed a request.")
    # read the blob into memory
    bl_object = obj.read()
    blob_to_read = BytesIO(bl_object)
    df = pd.read_csv(blob_to_read)
    logging.info("Reading blob csv with length:" + str(len(df.index)))
    # Continue to perform whatever logic is needed below