import asyncio
from datetime import datetime, timedelta
import threading
import azure.functions as func
from dateutil import parser
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings
from wrapperfunction.admin.model.crawl_status import CrawlingStatus
from wrapperfunction.admin.service import crawl_service
from wrapperfunction.core import config
from wrapperfunction.core.service import settings_service
from wrapperfunction.media_monitoring.service import media_service
from wrapperfunction.search.integration import aisearch_connector

# Define a function app blueprint for scheduling media crawling tasks
media_bp = func.Blueprint()
media_bp.function_name("schedule_media_crawl")

# Scheduled function to trigger crawling every day at midnight (UTC)
@media_bp.schedule(arg_name="CrawlingTimer", schedule="0 0 * * *")
async def daily_schedule_media_crawl(CrawlingTimer: func.TimerRequest):
    try:
        # Fetch crawling settings from the configuration
        entity_settings = settings_service.get_settings_by_entity(config.ENTITY_NAME)[0]
        media_settings = entity_settings.get("media_settings", None)
        urls = media_settings.get("crawling_urls", [])

        # Start crawling tasks for each URL asynchronously
        for index, url in enumerate(urls):
            thread = threading.Thread(
                target=setup_and_crawl,
                args=(url, index)  
                )
            thread.start()

    except Exception as e:
        print(f"Error during scheduled crawl: {e}")

# Function to handle crawling setup and execution
def setup_and_crawl(url: dict, index: int):
    try:
        # Parse last crawl date and determine the next scheduled crawl date
        last_crawl_date = parser.parse(url["last_crawl"]).date()
        crawl_days = timedelta(days=url["crawl_days"])
        next_crawl_date = last_crawl_date + crawl_days
        print(f"Crawling Status: {url['crawling_status']}, Last Crawl Date: {url['last_crawl']}, New Crawl Date: {next_crawl_date}" )

        # Check if the URL should be crawled today
        if next_crawl_date <= datetime.utcnow().date():
            url["crawling_status"] = CrawlingStatus.INPROGRESS.value
            print(f"Crawling Status: {url['crawling_status']}")
            settings_service.update_crawling_status(url["crawling_status"], index=index)
            print("Getting required data...")

            # Retrieve URLs and settings required for crawling
            data = get_crawl_required_data(url["crawl_settings"])

            # Proceed with crawling if there are URLs to crawl
            if data[0] and data[1]:
                print("Crawl Started...")
                print(data[0][0].link)
                res = crawl_service.crawl_urls(urls=data[0], settings=data[1])
                print(f"Scheduled URL Crawling results: {res}")
            else:
                print("No URLs to be crawled")

            # Update crawl status and last crawl date upon successful execution
            url["crawling_status"] = CrawlingStatus.SUCCESS.value
            url["last_crawl"] = datetime.utcnow().date()
            print(f"Crawling Status: {url['crawling_status']}",f"Last Crawl Date: {url['last_crawl']}")
            settings_service.update_crawling_status(
                url["crawling_status"], index, last_crawl_date
            )

    except Exception as e:
        url["crawling_status"] = CrawlingStatus.ERROR.value
        settings_service.update_crawling_status(url["crawling_status"], index=index)
        print(f"Error while crawling index {index}: {e}")
        return Exception(f"Error while crawling index {index}: {e}")

# Function to extract required crawl data (URLs & settings) from the provided configuration
def get_crawl_required_data(crawl_settings_data: dict):
    crawl_settings = crawl_settings_data.get("settings", None)
    urls_config = crawl_settings_data.get("urls", [])

    # Create a list of CrawlRequestUrls objects for each URL in the configuration
    urls = [
        CrawlRequestUrls(
            link=url["link"],
            cookies=url["cookies"],
            headers=url["headers"],
            internal=url["internal"],
            payload=url["payload"],
            settings=url["settings"],
        )
        for url in urls_config
    ]

    # Create a CrawlSettings object with crawling configuration
    settings = CrawlSettings(
        containerName=crawl_settings["containerName"],
        deep=crawl_settings["deep"],
        selectors=crawl_settings["selectors"],
        mediaCrawling=crawl_settings["mediaCrawling"],
        topics=crawl_settings["topics"],
    )

    return urls, settings

# Scheduled function to run the media indexer every day at 8 AM (UTC)
@media_bp.schedule(arg_name="RunMediaIndexer", schedule="0 8 * * *")
async def schedule_media_crawl(RunMediaIndexer: func.TimerRequest):
    # Retrieve media settings from configuration
    entity_settings = settings_service.get_settings_by_entity(config.ENTITY_NAME)[0]
    media_settings = entity_settings.get("media_settings", None)
    urls = media_settings.get("crawling_urls", [])

    # Check if any URLs are still being crawled
    run_indexer = all(url["crawling_status"] != CrawlingStatus.INPROGRESS.value for url in urls)

    if run_indexer:
        # Retrieve index and indexer information
        info = config.get_media_info()
        index_info = aisearch_connector.get_index_info(info["index_name"])
        indexer_name = index_info.indexer_name
        index_name = index_info.index_name

        # Run the search indexer to update indexed data
        search_indexer_client = aisearch_connector.get_search_indexer_client()
        search_indexer_client.run_indexer(indexer_name)

        # Start a background thread to monitor the indexer and apply custom skills
        thread = threading.Thread(
            target=media_service.monitor_indexer,
            args=(search_indexer_client, indexer_name, index_name),
        )
        thread.start()