from pydantic import BaseModel
from typing import List

from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings


class MediaCrawlRequest(BaseModel):
    settings: CrawlSettings
    urls: List[CrawlRequestUrls]