from pydantic import BaseModel

class searchCriteria(BaseModel):
    query: str
    facet: str = None
    sort: str = None
    page_size: int=1000000
    page_number: int=1
    k: int=50