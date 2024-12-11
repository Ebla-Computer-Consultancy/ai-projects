from enum import Enum
from pydantic import BaseModel


class CrawlSettings(BaseModel):
    deep: bool = False
    selectors: set[str] = set()
    mediaCrawling: bool = False
    topics: list[str] = set()

class IndexingType(Enum):
    CRAWLED = "crawled"
    NOT_CRAWLED = "notcrawled"
    GENERATED = "generated"