from fastapi import HTTPException
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.core import config


def get_user(username):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_TABLE,f"username eq '{username}'",conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

def get_user_permissions(user_id):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_PER_TABLE,f"user eq '{user_id}'",conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))