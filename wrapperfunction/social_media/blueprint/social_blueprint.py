from typing import List
import azure.functions as func
from wrapperfunction.core import config
from wrapperfunction.core.service import settings_service
from wrapperfunction.social_media.model.x_model import XSearch
from wrapperfunction.social_media.service import x_service


# Define a function app blueprint for scheduling media crawling tasks
social_bp = func.Blueprint()
social_bp.function_name("schedule_social_crawl")

# Scheduled function to trigger crawling every day at midnight (UTC)
@social_bp.schedule(arg_name="CrawlingTimer", schedule="08 * * * *")
async def daily_schedule_x_crawl(CrawlingTimer: func.TimerRequest):
    try:
        entity_settings = settings_service.get_settings_by_entity(config.ENTITY_NAME)[0]
        media_settings = entity_settings.get("media_settings", None)
        x_crawl_settings = media_settings.get("x_crawling", [])
        if len(x_crawl_settings) > 0:
            data = get_x_data(x_crawl_settings)
            await x_service.x_multi_search(data=data)
    except Exception as e:
        raise Exception(str(e))

def get_x_data(data_list: list) -> List[XSearch]:
    try:
        return [XSearch(query=data.get("query"),
                        start_time=data.get("start_time",None),
                        end_time=data.get("end_time",None),
                        max_results=data.get("max_results",10)) for data in data_list]
    except Exception as e:
        raise Exception(str(e))
        