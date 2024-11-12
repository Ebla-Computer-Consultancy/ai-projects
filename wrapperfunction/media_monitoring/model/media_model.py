from typing import List
from pydantic import BaseModel

class MediaRequest(BaseModel):
    search_text: str 

class MediaCrawlRequest(BaseModel):
    topics: List[str]
    urls: List[str]

class SkillRecord(BaseModel):
    recordId: str
    data: dict
class CustomSkillRequest(BaseModel):
    values: List[SkillRecord]
      
