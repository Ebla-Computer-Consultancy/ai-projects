from pydantic import BaseModel
from typing import List


class MediaCrawlRequest(BaseModel):
    topics: List[str]
    urls: List[str]