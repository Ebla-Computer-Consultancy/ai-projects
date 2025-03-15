import json
from typing import List
import uuid
from fastapi import HTTPException
from wrapperfunction.core import config
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.social_media.model.x_model import XSearch

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

def update_schedule_settings(new_settings: dict):
    try:
        entity_settings = get_settings_by_entity(config.ENTITY_NAME)[0]
        entity_settings["media_settings"]["crawling_urls"] = new_settings
        return update_bot_settings(entity_settings)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_crawling_status(new_status: str,index: int,new_last_crawl=None):
    try:
        entity_settings = get_settings_by_entity(config.ENTITY_NAME)[0]
        entity_settings["media_settings"]["crawling_urls"][index]["crawling_status"] = new_status
        if new_last_crawl:
            entity_settings["media_settings"]["crawling_urls"][index]["last_crawl"] = new_last_crawl
        return update_bot_settings(entity_settings)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_x_crawling_settings(data_list: List[XSearch]):
    try:
        entity_settings = get_settings_by_entity(config.ENTITY_NAME)[0]
        for data in data_list:
            entity_settings["media_settings"]["x_crawling"].append({
                "query":data.query,
                "max_results":data.max_results,
                "start_time":data.start_time,
                "end_time":data.end_time
            })
        
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