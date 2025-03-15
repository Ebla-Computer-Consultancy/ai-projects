from pydantic import BaseModel

class MediaRequest(BaseModel):
    search_text: str
    index_date_from: str = None
    index_date_to: str = None
    news_date_from: str = None
    news_date_to: str = None
    tags: list = None

class MediaInfo(BaseModel):
    index_name: str = "media"
    container_name: str = "media"
    reports_container_name: str = "media-reports"
    
