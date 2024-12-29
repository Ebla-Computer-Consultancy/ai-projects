from typing import Any
from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    field: str
    value: Any

class SettingCreate(BaseModel):
    data: dict 