from pydantic import BaseModel

class CrawlRequestUrls(BaseModel):
    link: str
    headers: dict = {}
    cookies: dict = {}
    payload: dict = None
