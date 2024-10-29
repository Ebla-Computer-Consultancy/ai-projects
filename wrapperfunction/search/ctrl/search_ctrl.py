from wrapperfunction.search.model.search_criterial import searchCriteria
from fastapi import APIRouter
import wrapperfunction.search.service.search_service as searchservice

router = APIRouter()

@router.post("/search")
def search(rs: searchCriteria):
    return searchservice.search(rs)

