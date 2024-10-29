from wrapperfunction.search.model.search_criterial import searchCriteria
from fastapi import APIRouter
import wrapperfunction.search.service.search_service as searchservice

router = APIRouter()

@router.post("/search/{bot_name}")
def search(bot_name: str,rs: searchCriteria):
    return searchservice.search(bot_name,rs)

