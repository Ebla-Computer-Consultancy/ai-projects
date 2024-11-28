from pydantic import BaseModel

class IndexerRequest(BaseModel):
    index_name: str
