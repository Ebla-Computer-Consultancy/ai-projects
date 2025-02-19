from typing import List
from fastapi import APIRouter
from wrapperfunction.social_media.model.x_model import XSearch
from wrapperfunction.social_media.service import x_service

router = APIRouter()

@router.post("/x-search")
async def get_x_search_results(body: List[XSearch]):
    try:
        return x_service.x_multi_search(data=body)
    except Exception as e:
        raise Exception(f"{str(e)}")