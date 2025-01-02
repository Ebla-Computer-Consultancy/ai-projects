from enum import Enum
from pydantic import BaseModel

from wrapperfunction.core import config


class CrawlSettings(BaseModel):
    deep: bool = False
    selectors: set[str] = set()
    mediaCrawling: bool = False
    topics: list[str] = set()
    containerName: str = config.BLOB_CONTAINER_NAME
    main_lang: str = "ar"

class IndexingType(Enum):
    CRAWLED = "crawled"
    NOT_CRAWLED = "notcrawled"
    GENERATED = "generated"