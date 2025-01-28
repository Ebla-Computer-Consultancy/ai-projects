import re
import uuid
from fastapi import HTTPException, status
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.core import config


def get_user_by_username(username):
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

def get_full_user_permissions_info(user_id):
    try:
        res = []
        user_permissions = get_user_permissions(user_id)
        all_permissions = get_permissions()
        user_per_id = [per["permission_id"] for per in user_permissions]
        res = [per for per in all_permissions if per["_id"] in user_per_id]
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

async def add_permission_to_user(user_id: str, per_ids: list):
    try:  
        for per_id in per_ids:
            if len(get_permission_by_id(per_id)) > 0:
                entity = {
                        "PartitionKey":str(uuid.uuid4()),
                        "RowKey":str(uuid.uuid4()),
                        "user_id":str(user_id),
                        "permission_id":str(per_id)   
                    }
                res = await db_connector.add_entity(config.COSMOS_AUTH_USER_PER_TABLE,entity=entity)
            else:
                raise Exception(f"Permission with id:'{per_id}' Not Found")
            return res
        else:
            raise Exception("User Not Found")
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

async def update_permission_to_user(user_id: str, new_per_ids: list):
    try:
        if len(get_user_by_id(user_id)) > 0:
            old_per_ids = [permission["permission_id"] for permission in get_user_permissions(user_id)]
            old_set = set(old_per_ids)
            new_set = set(new_per_ids)

            added_ids = list(new_set - old_set)
            removed_ids = list(old_set - new_set)
            add_res = None
            remove_res = None
            if len(added_ids) > 0:
                add_res = await add_permission_to_user(user_id,added_ids)
            if len(removed_ids) > 0:
                remove_res = remove_user_permission(user_id,removed_ids)
                
            return {"added_permissions": add_res,"removed_permissions":remove_res}
        else:
            raise Exception("User Not Found")
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

async def add_user(username: str):
    try:
        if validate_username(username)[0]:
            if len(get_user_by_username(username)) < 1:
                
                entity = {
                    "PartitionKey":str(uuid.uuid4()),
                    "RowKey":str(uuid.uuid4()),
                    "_id":str(uuid.uuid4()),
                    "username":username,
                    "never_expire": False,
                    "refresh_token": ""
                }
                res = await db_connector.add_entity(config.COSMOS_AUTH_USER_TABLE,entity)
                return res
            else:
                raise Exception("User Already Exist")
        else:
            raise Exception(f"'{username}' is not a valid username")
    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def remove_user_permission(user_id: str,per_ids: list):
    try:
        for per_id in per_ids:
            entity = get_user_permission(user_id,per_id)
            if len(entity) > 0:
                res =  db_connector.delete_entity(config.COSMOS_AUTH_USER_PER_TABLE,entity[0])
            else:
                raise Exception(f"Permission with id:'{per_id}' Not Found")
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


def validate_username(username: str):
    
    if not username.strip():
        return False, "Username cannot be empty."
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters."
    elif not username.isalnum():
        return False, "Username can only contain letters and numbers."
    return True, "Valid username."

def validate_password(password: str):
    
    if not password.strip():
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, "Valid password."
