from fastapi import APIRouter, Request
from wrapperfunction.chat_history.model.loclization_entity import LocalizationEntity, localizationPayload
import wrapperfunction.chat_history.service.localization_service as localizationservice
from typing import Optional

router = APIRouter()


@router.post("/", response_model=dict)
async def create_label(label: localizationPayload):
    return await localizationservice.create_label(label)


@router.get("/{lookup_key}", response_model=dict)
async def read_label(lookup_key: str):
    return await localizationservice.read_label(lookup_key)


@router.put("/{lookup_key}", response_model=dict)
async def update_label(lookup_key: str, label: localizationPayload):
    return await localizationservice.update_label(lookup_key,label)


@router.delete("/{lookup_key}", response_model=dict)
async def delete_label(lookup_key: str):
    return await localizationservice.delete_label(lookup_key)


