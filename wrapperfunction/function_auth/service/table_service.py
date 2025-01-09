import random
import uuid
from fastapi import HTTPException, status
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.core import config


def get_user(username):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_TABLE,f"username eq '{username}'",conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_user_by_token(token, username):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_TABLE,f"refresh_token eq '{token}' and username eq '{username}'",conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_user_permissions(user_id):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_PER_TABLE,f"user eq '{user_id}'",conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_permission_by_key(key):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_PERMISSION_TABLE,f"key eq '{key}'",conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def get_permission_by_name(name):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_PERMISSION_TABLE,f"name eq '{name}'",conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def update_refresh_token(entity, token):
    try:
        entity["refresh_token"] = token
        res =  db_connector.update_entity(config.COSMOS_AUTH_USER_TABLE,entity,conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

async def add_permission_to_user(username, per_id):
    try:
        user = get_user(username)
        per = get_permission_by_key(per_id)
        entity = {
            "PartitionKey":str(uuid.uuid4()),
            "RowKey":str(uuid.uuid4()),
            "user":user[0]["user-id"],
            "permission":per_id
        }
        res = await db_connector.add_entity(config.COSMOS_AUTH_USER_PER_TABLE,entity=entity,conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

async def add_permission_to_table(name, en, ar):
    try:
        key = 0
        while True:
            k = str(random.randint(60, 200))
            if len(get_permission_by_key(key=k)) == 0:
               key = k
               break 
        entity = {
            "PartitionKey":str(uuid.uuid4()),
            "RowKey":str(uuid.uuid4()),
            "key": key,
            "name":name,
            "en_name":en,
            "ar_name":ar
        }
        res = await db_connector.add_entity(config.COSMOS_AUTH_PERMISSION_TABLE,entity=entity,conn_str=config.COSMOS_AUTH_CONNECTION_STRING)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))