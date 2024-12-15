from pydantic import BaseModel

from wrapperfunction.admin.model.crawl_settings import CrawlSettings

class CrawlRequestUrls(BaseModel):
    link: str
    headers: dict = {}
    cookies: dict = {}
    payload: dict = None
    settings: CrawlSettings
