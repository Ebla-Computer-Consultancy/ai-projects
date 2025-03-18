from datetime import datetime
from uuid import uuid4
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class LocalizationPropertyName(Enum):
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    LOCALIZATION_ID = "localization_id"
    TIMESTAMP = "timestamp"
    LOOKUP_KEY = "lookup_key"
    AR_NAME = "ar_name"
    EN_NAME = "en_name"



class LocalizationEntity:
    def __init__(self, localization_id:str, lookup_key: str, ar_name: str, en_name: str):
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.localization_id = localization_id
        self.timestamp = datetime.now().isoformat()
        self.lookup_key = lookup_key
        self.ar_name = ar_name
        self.en_name = en_name
    
    def set(self, lookup_key: str, ar_name: str, en_name: str ):
        self.timestamp = datetime.now().isoformat()
        self.lookup_key = lookup_key
        self.ar_name = ar_name
        self.en_name = en_name

    def to_dict(self):
        return {
            LocalizationPropertyName.PARTITION_KEY.value: self.partition_key,
            LocalizationPropertyName.ROW_KEY.value: self.row_key,
            LocalizationPropertyName.LOCALIZATION_ID.value: self.localization_id,
            LocalizationPropertyName.TIMESTAMP.value: self.timestamp,
            LocalizationPropertyName.LOOKUP_KEY.value: self.lookup_key,
            LocalizationPropertyName.AR_NAME.value: self.ar_name,
            LocalizationPropertyName.EN_NAME.value: self.en_name
        }


class localizationPayload(BaseModel):
    lookup_key: Optional[str] = None
    ar_name: Optional[str] = None
    en_name: Optional[str]=None
    def to_dict(self):
        return {"lookup_key":self.lookup_key,
                "ar_name": self.ar_name,
                "en_name": self.en_name}
