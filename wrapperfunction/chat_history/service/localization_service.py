from fastapi import HTTPException
from wrapperfunction.chat_history.model.loclization_entity import LocalizationEntity,LocalizationPropertyName, localizationPayload
from wrapperfunction.chat_history.integration.cosmos_db_connector import *
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from typing import Optional
from wrapperfunction.core import config
import uuid


async def create_label(label: Optional[localizationPayload]=None):
    localization_id = str(uuid.uuid4())
    label_data = label.to_dict()
    local_entity = LocalizationEntity(localization_id,label_data["lookup_key"],label_data["ar_name"],label_data["en_name"])
    await add_entity(table_name=config.LOCALIZATION_TABLE_NAME, entity=local_entity.to_dict())
    return ServiceReturn(
        status=StatusCode.SUCCESS, message=f"The new localization item has successfully Created"
        ).to_dict()


async def read_label(lookup_key: str):
    filter_expression = f"{LocalizationPropertyName.LOOKUP_KEY.value} eq '{lookup_key}'"
    entities = get_entities(table_name=config.LOCALIZATION_TABLE_NAME, filter_expression=filter_expression)
    if entities:
        return ServiceReturn(
        status=StatusCode.SUCCESS,message= "Done",data= entities[0]
        ).to_dict()
    else:
        return ServiceReturn(
        status=StatusCode.NOT_FOUND,message= "This localization item not found"
        ).to_dict()
    
async def update_label(lookup_key: str, label: Optional[localizationPayload]=None):
    filter_expression = f"{LocalizationPropertyName.LOOKUP_KEY.value} eq '{lookup_key}'"
    entities = get_entities(table_name=config.LOCALIZATION_TABLE_NAME, filter_expression=filter_expression)
    if entities:
        label_data = label.to_dict()
        entities[0].update(lookup_key=label_data["lookup_key"], ar_name=label_data["ar_name"], en_name= label_data["en_name"])
        update_entity(table_name=config.LOCALIZATION_TABLE_NAME, entity=entities[0])
        return ServiceReturn(
        status=StatusCode.SUCCESS,message= "Updated Done" ,data= entities[0]
        ).to_dict()
    else:
        return ServiceReturn(
        status=StatusCode.NOT_FOUND,message= "This localization item not found"
        ).to_dict()


async def delete_label(lookup_key: str):
    filter_expression = f"{LocalizationPropertyName.LOOKUP_KEY.value} eq '{lookup_key}'"
    entities = get_entities(table_name=config.LOCALIZATION_TABLE_NAME, filter_expression=filter_expression)
    if entities:
        delete_entity(table_name=config.LOCALIZATION_TABLE_NAME, entity=entities[0])
        return ServiceReturn(
        status=StatusCode.SUCCESS,message= "The localization item has successfully Deleted"
        ).to_dict()
    else:
        return ServiceReturn(
        status=StatusCode.NOT_FOUND,message= "This localization item not found"
        ).to_dict()


