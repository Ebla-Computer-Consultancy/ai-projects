from pydantic import BaseModel

class MediaRequest(BaseModel):
    search_text: str 
