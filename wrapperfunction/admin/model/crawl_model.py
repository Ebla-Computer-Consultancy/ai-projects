from typing import List
from pydantic import BaseModel

# class CrawlRequest(BaseModel):
#     new_content_file:

class MediaRequest(BaseModel):
    search_text: str 

class MediaCrawlRequest(BaseModel):
    topics: List[str]
    urls: List[str] 
    
class IndexerRequest(BaseModel):
    name: str