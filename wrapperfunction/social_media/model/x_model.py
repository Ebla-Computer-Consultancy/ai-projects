from pydantic import BaseModel


class XSearch(BaseModel):
    query: str
    start_time: str = None
    end_time: str = None
    max_results: int = 10