from typing import Optional
from pydantic import BaseModel


class XSearch(BaseModel):
    query: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    max_results: int = 10