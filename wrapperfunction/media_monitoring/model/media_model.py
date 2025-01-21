from pydantic import BaseModel

class MediaRequest(BaseModel):
    search_text: str 
    search_text: str
    index_date_from: str = None
    index_date_to: str = None
    news_date_from: str = None
    news_date_to: str = None
    tags: list = None
