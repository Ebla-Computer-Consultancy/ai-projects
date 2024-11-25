from typing import List
from pydantic import BaseModel

# class CrawlRequest(BaseModel):
#     new_content_file:
    
class IndexerRequest(BaseModel):
    name: str