from typing import List
from fastapi import APIRouter
from wrapperfunction.social_media.integration import x_connector
from wrapperfunction.social_media.model.x_model import XSearch

router = APIRouter()

@router.post("/x-search")
async def get_x_search_results(body: List[XSearch]):
    try:
        return x_connector.x_multi_search(data=body)
    except Exception as e:
        raise Exception(f"{str(e)}")