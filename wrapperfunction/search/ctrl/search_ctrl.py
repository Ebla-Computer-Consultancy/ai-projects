from fastapi import APIRouter
from wrapperfunction.search.model.search_criterial import searchCriteria
import wrapperfunction.search.service.search_service as search_service

router = APIRouter()

@router.post("/search/{bot_name}")
def search(bot_name: str,rs: searchCriteria):
    return search_service.search(bot_name,rs)

