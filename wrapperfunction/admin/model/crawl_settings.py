from pydantic import BaseModel


class CrawlSettings(BaseModel):
    deep: bool = False
    selectors: set[str] = set()
