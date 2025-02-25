from enum import Enum
from pydantic import BaseModel

class IndexerRequest(BaseModel):
    index_name: str

class IndexerLastRunStatus(Enum):
    IN_PROGRESS = "inProgress"
    SUCCESS = "success"
    RESET = "reset"
    TRANSIENT_FAILURE = "transientFailure"
    PERSISTENT_FAILURE = "persistentFailure"

class IndexInfo(BaseModel):
    # index_details: dict
    index_name: str
    indexer_name: str
    data_source_name: str
    data_storage_type: str
    data_storage_name: str
    skillset_name: str