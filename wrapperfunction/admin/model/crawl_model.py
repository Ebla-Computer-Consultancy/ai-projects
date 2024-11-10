from pydantic import BaseModel

# class CrawlRequest(BaseModel):
#     new_content_file:

class MediaRequest(BaseModel):
    search_text: str 

class MediaCrawlRequest(BaseModel):
    topic: str
    url: str 