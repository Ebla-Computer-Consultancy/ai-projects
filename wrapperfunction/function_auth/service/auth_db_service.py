import random
import uuid
from fastapi import HTTPException, status
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.core import config


def get_user_by_name(username):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_TABLE,f"username eq '{username}'")
        for user in res:
            del user["refresh_token"]
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_user_by_id(id):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_TABLE,f"_id eq '{id}'")
        for user in res:
            del user["refresh_token"]
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_user_by_refresh_token(token, user_id):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_TABLE,f"refresh_token eq '{token}' and _id eq '{user_id}'")
        for user in res:
            del user["refresh_token"]
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_user_permissions(user_id):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_PER_TABLE,f"user_id eq '{user_id}'")
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_user_permission(user_id, per_id):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_PER_TABLE,f"user_id eq '{user_id}' and permission_id eq '{per_id}'")
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_permission_by_id(id):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_PERMISSION_TABLE,f"_id eq '{id}'")
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def get_permission_by_key(key):
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_PERMISSION_TABLE,f"name eq '{key}'")
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def update_refresh_token(entity, token):
    try:
        entity["refresh_token"] = token
        res =  db_connector.update_entity(config.COSMOS_AUTH_USER_TABLE,entity)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

async def add_permission_to_user(user_id, per_id):
    try:
        if len(get_user_by_id(user_id)) > 0 and len(get_permission_by_id(per_id)) > 0:
            entity = {
                "PartitionKey":str(uuid.uuid4()),
                "RowKey":str(uuid.uuid4()),
                "user_id":str(user_id),
                "permission_id":str(per_id),
                
            }
            res = await db_connector.add_entity(config.COSMOS_AUTH_USER_PER_TABLE,entity=entity)
            return res
        else:
            raise Exception("User/Permission Not Found")
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_permissions():
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_PERMISSION_TABLE)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_users():
    try:
        res =  db_connector.get_entities(config.COSMOS_AUTH_USER_TABLE)
        for user in res:
            del user["refresh_token"]
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def update_user(user):
    try:        
        res =  db_connector.update_entity(config.COSMOS_AUTH_USER_TABLE, entity=user)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

async def add_user(username):
    try:
        id = 0 
        users = get_users()
        if len(users) > 0:
            max_id = int(users[0]["_id"])
            for user in users:
                if max_id < int(user["_id"]):
                    max_id = int(user["_id"])
            id = max_id + 1
        entity = {
            "PartitionKey":str(uuid.uuid4()),
            "RowKey":str(uuid.uuid4()),
            "_id":str(id),
            "username":username,
            "never_expire": False,
            "refresh_token": ""
        }
        res = await db_connector.add_entity(config.COSMOS_AUTH_USER_TABLE,entity)
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def remove_user_permission(user_id,per_id):
    try:
        entity = get_user_permission(user_id,per_id)
        res =  db_connector.delete_entity(config.COSMOS_AUTH_USER_PER_TABLE,entity[0])
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def delete_user(user_id):
    try:
        entity = get_user_by_id(user_id)
        res =  db_connector.delete_entity(config.COSMOS_AUTH_USER_TABLE,entity[0])
        return res
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))