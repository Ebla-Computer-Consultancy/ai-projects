import json
import uuid
from fastapi import HTTPException
from wrapperfunction.core import config
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.core.model.schedule_days_model import ScheduleDays

def get_all_settings():
    try:
        res =  db_connector.get_entities(config.COSMOS_SETTINGS_TABLE)
        return format_settings(res)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def get_settings_by_entity(entity_name):
    try:
        res =  db_connector.get_entities(config.COSMOS_SETTINGS_TABLE,f"entity_name eq '{entity_name}'")
        return format_settings(res)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_chatbot_settings_by_entity(entity_name,chatbot_name):
    try:
        res =  db_connector.get_entities(config.COSMOS_SETTINGS_TABLE,f"entity_name eq '{entity_name}' and chatbot_name eq '{chatbot_name}'")
        return format_settings(res)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def update_bot_settings(entity):
    try:
        res =  db_connector.update_entity(config.COSMOS_SETTINGS_TABLE,add_format_settings(entity))
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_schedule_settings(new_settings: dict,days: int):
    try:
        entity_settings = get_settings_by_entity(config.ENTITY_NAME)[0]
        entity_settings["media_settings"][f'{ScheduleDays(days).name}'] = new_settings
        return update_bot_settings(entity_settings)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def add_setting(entity):
    try:
        entity["PartitionKey"] = str(uuid.uuid4())
        entity["RowKey"] = str(uuid.uuid4())
        res = await db_connector.add_entity(config.COSMOS_SETTINGS_TABLE,add_format_settings(entity))
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def delete_bot_settings(entity):
    try:
        res =  db_connector.delete_entity(config.COSMOS_SETTINGS_TABLE,entity)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def format_settings(settings: list):
    for setting in settings:
        for key, value in setting.items():
            if str(value).startswith(tuple(["{", "["])):
                setting[key] = json.loads(value)
    return settings

def add_format_settings(setting: list):
    for key, value in setting.items():
        if isinstance(value, (list, dict)):
            setting[key] = json.dumps(value, ensure_ascii=False)
    return setting