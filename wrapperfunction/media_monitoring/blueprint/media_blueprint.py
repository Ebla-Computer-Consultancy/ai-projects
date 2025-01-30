import azure.functions as func

from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings
from wrapperfunction.core import config
from wrapperfunction.core.service import settings_service
from wrapperfunction.media_monitoring.service import media_service


media_bp = func.Blueprint()
media_bp.function_name("schedule_media_crawl")

@media_bp.schedule(arg_name="OneDayCrawlingTimer",schedule="0 0 */1 * *")
async def one_day_media_crawl(OneDayCrawlingTimer: func.TimerRequest):
    try:
        print("One Day Crawl: Getting required data...")
        entity_settings = settings_service.get_settings_by_entity(config.ENTITY_NAME)[0]
        media_settings = entity_settings.get("media_settings", None)
        DayUrls = media_settings.get("oneDayUrls", None)
        if DayUrls:
            crawl_settings = DayUrls.get("settings", None)
            urls_config = DayUrls.get("urls", [])
            
            urls = [CrawlRequestUrls(
                link=url["link"],
                cookies=url["cookies"],
                headers=url["headers"],
                internal=url["internal"],
                payload=url["payload"],
                settings=url["settings"]
                ) for url in urls_config]
            
            settings = CrawlSettings(
                containerName=crawl_settings["containerName"],
                deep=crawl_settings["deep"],
                selectors=crawl_settings["selectors"],
                mediaCrawling=crawl_settings["mediaCrawling"],
                topics=crawl_settings["topics"]
                )
        
            print("One Day Crawl: Crawl Started")
        
            res = await media_service.crawl_urls(urls=urls,settings=settings)
            print(f"One Day Crawl: Scheduled URL's Crawling results: {res}")
        else:
            print("One Day Crawl: No Urls to be crawled")
    except Exception as e:
        print(f"One Day Crawl: Error during scheduled crawl: {e}")

@media_bp.schedule(arg_name="FiveDaysCrawling",schedule="0 0 */5 * *")
async def five_day_media_crawl(FiveDaysCrawling: func.TimerRequest):
    try:
        print("Five Days Crawl: Getting required data...")
        entity_settings = settings_service.get_settings_by_entity(config.ENTITY_NAME)[0]
        media_settings = entity_settings.get("media_settings", None)
        DaysUrls = media_settings.get("fiveDaysUrls", None)
        if DaysUrls:
            crawl_settings = DaysUrls.get("settings", None)
            urls_config = DaysUrls.get("urls", [])
            
            urls = [CrawlRequestUrls(
                link=url["link"],
                cookies=url["cookies"],
                headers=url["headers"],
                internal=url["internal"],
                payload=url["payload"],
                settings=url["settings"]
                ) for url in urls_config]
            
            settings = CrawlSettings(
                containerName=crawl_settings["containerName"],
                deep=crawl_settings["deep"],
                selectors=crawl_settings["selectors"],
                mediaCrawling=crawl_settings["mediaCrawling"],
                topics=crawl_settings["topics"]
                )
        
            print("Five Days Crawl: Crawl Started")
        
            res = await media_service.crawl_urls(urls=urls,settings=settings)
            print(f"Five Days Crawl: Scheduled URL's Crawling results: {res}")
        else:
            print("Five Days Crawl: No Urls to be crawled")
    except Exception as e:
        print(f"Five Days Crawl: Error during scheduled crawl: {e}")
        
@media_bp.schedule(arg_name="TenDaysCrawling",schedule="0 0 */10 * *")
async def ten_day_media_crawl(TenDaysCrawling: func.TimerRequest):
    try:
        print("Ten Days Crawl: Getting required data...")
        entity_settings = settings_service.get_settings_by_entity(config.ENTITY_NAME)[0]
        media_settings = entity_settings.get("media_settings", None)
        DaysUrls = media_settings.get("tenDaysUrls", None)
        if DaysUrls:
            crawl_settings = DaysUrls.get("settings", None)
            urls_config = DaysUrls.get("urls", [])
            
            urls = [CrawlRequestUrls(
                link=url["link"],
                cookies=url["cookies"],
                headers=url["headers"],
                internal=url["internal"],
                payload=url["payload"],
                settings=url["settings"]
                ) for url in urls_config]
            
            settings = CrawlSettings(
                containerName=crawl_settings["containerName"],
                deep=crawl_settings["deep"],
                selectors=crawl_settings["selectors"],
                mediaCrawling=crawl_settings["mediaCrawling"],
                topics=crawl_settings["topics"]
                )
        
            print("Ten Days Crawl: Crawl Started")
        
            res = await media_service.crawl_urls(urls=urls,settings=settings)
            print(f"Ten Days Crawl: Scheduled URL's Crawling results: {res}")
        else:
            print("Ten Days Crawl: No Urls to be crawled")
    except Exception as e:
        print(f"Ten Days Crawl: Error during scheduled crawl: {e}")