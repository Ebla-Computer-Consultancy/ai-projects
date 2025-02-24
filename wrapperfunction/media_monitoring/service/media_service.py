import asyncio
import copy
from datetime import datetime
import time
from typing import List
import uuid
from dateutil import parser
from fastapi import HTTPException
from wrapperfunction.admin.integration import imageanalytics_connector
from wrapperfunction.admin.integration import textanalytics_connector
from wrapperfunction.admin.service.blob_service import generate_blob_sas_url
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings, IndexingType
from wrapperfunction.admin.service.blob_service import append_blob
from wrapperfunction.admin.service.crawl_service import crawl_urls
from wrapperfunction.chatbot.integration.openai_connector import  chat_completion
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.admin.model.textanalytics_model import TextAnalyticsKEYS as tak
from wrapperfunction.core.service import settings_service
from wrapperfunction.function_auth.service import validation_service
from wrapperfunction.search.integration import aisearch_connector
from wrapperfunction.search.integration.aisearch_connector import get_search_indexer_client, search_query
from azure.search.documents.indexes.models import SearchIndexer
from azure.search.documents.indexes import SearchIndexerClient
from wrapperfunction.search.model.indexer_model import IndexerLastRunStatus
from wrapperfunction.search.service.search_service import update_index
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector

async def generate_report(search_text: str,index_date_from = None,index_date_to = None,news_date_from = None,news_date_to = None, tags: List[str] = None):
    try:
        user_message = f"write a long report in about 2 pages(reach the max)..about:{search_text}.",
        # Prepare Filter Expression
        filter_exp = concat_exp(
            prepare_dates_exp(index_date_from,index_date_to,news_date_from,news_date_to),
            prepare_tags_exp(tags)
            )
        # Load Chatbot Settings      
        chat_settings = config.load_chatbot_settings(bot_name="media")
        chat_settings.custom_settings.filter = filter_exp
        # Setup History 
        chat_history = [{"role": "system", "content": chat_settings.system_message}]
        chat_history.append({"role": "user", "content": str(user_message)})

        chat_res = chat_completion(
            chatbot_setting=chat_settings,
            chat_history=chat_history
        )
        # Renaming Title field & Collect All references urls
        ref = []  
        for citation in chat_res["message"]["context"]["citations"]:
            if citation["url"] is not None:
                citation["title"] = citation["url"]
                ref.append(citation["url"])
        # Rename the report
        report_file_name = search_text.replace(" ","_")
        # Get media storage info info 
        info = config.get_media_info()
        # Push the file to the Azure container
        append_blob(blob=chat_res["message"]["content"],
                    metadata_3=IndexingType.GENERATED.value,
                    folder_name=config.SUBFOLDER_NAME,
                    container_name= info["reports_container_name"],
                    blob_name=f"{report_file_name}.txt")
        
        # Generate SAS url for the report file
        sas_url = generate_blob_sas_url(container_name= info["reports_container_name"],
                                            blob_name=f"{config.SUBFOLDER_NAME}/{report_file_name}.txt")
        return ServiceReturn(
            status=StatusCode.CREATED,
            message=f"{search_text} Report Generated Successfully",
            data={
                "report_url": sas_url,
                "references":ref,
                "final_response": chat_res 
            }
        ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
async def media_crawl(urls: list[CrawlRequestUrls], settings: CrawlSettings):
    try:
        # Crawling
        crawl_urls(
            urls,
            settings
        )
        # Indexer
        info = config.get_media_info()
        index_info = aisearch_connector.get_index_info(info["index_name"])
        indexer_name = index_info.indexer_name
        search_indexer_client = get_search_indexer_client()
        # search_indexer_client.run_indexer(indexer_name)
        status = search_indexer_client.get_indexer_status(indexer_name)
        
        print(f"URL's:{urls} | Topics:{settings.topics} crawled successfully")
        # Return Response
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            message=f"URL's:{urls} | Topics:{settings.topics} crawled successfully", 
                            data=status.last_result.status
                        ).to_dict()
    except Exception as e:
        raise Exception(f"{str(e)}")

def prepare_tags_exp(tags: list):
    if tags is not None:
        return " or ".join(filter(None, [f"keyphrases/any(tag: tag eq '{tag}') or locations/any(tag: tag eq '{tag}') or organizations/any(tag: tag eq '{tag}')" for tag in tags]))
    return None

def prepare_dates_exp(index_date_from, index_date_to, news_date_from, news_date_to):
    index_exp = " and ".join(filter(None, [f"index_date ge {index_date_from}" if index_date_from else None, f"index_date le {index_date_to}" if index_date_to else None]))
    news_exp = " and ".join(filter(None, [f"news_date ge {news_date_from}" if news_date_from else None, f"news_date le {news_date_to}" if news_date_to else None]))
  
    return " and ".join(filter(None, [index_exp, news_exp]))

def concat_exp(date_exp,tag_exp):
    return " and ".join(filter(None, [date_exp, tag_exp]))
      
def monitor_indexer(indexer_client: SearchIndexerClient, indexer_name: str, index_name: str):
    try:
        retries = 0
        while True:
            status = indexer_client.get_indexer_status(indexer_name)
            print(f"Checking status: {status.last_result.status}")
            
            if status.last_result.status != IndexerLastRunStatus.IN_PROGRESS.value:
                asyncio.create_task(
                    apply_skills_on_index(index_name)
                )
                break
            time.sleep(10)
            retries += 1
    except Exception as e:
        print(f"Error while monitoring indexer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while monitoring indexer: {str(e)}")

async def apply_skills_on_index(index_name: str):
    try:
        start_time = time.time()
        results = search_query(search_text="*",search_index=index_name, k=1000)
        docs = 0
        for index in results["rs"]:
            update = False
            index["index_date"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
            chunk = index["chunk"]
            if chunk is not None:
                if index["language"] is None:
                    detected_language = textanalytics_connector.detect_language(messages=[chunk])
                    index["language"] = detected_language[tak.LANGUAGE_ISO6391_NAME.value]
                    update = True
                    
                if index["sentiment"] is None:
                    sentiment = textanalytics_connector.analyze_sentiment(messages=[chunk])
                    index["sentiment"] = sentiment
                    update = True
                
                if len(index["keyphrases"]) == 0:
                    key_phrases = textanalytics_connector.extract_key_phrases(messages=[chunk],language=index["language"])
                    index["keyphrases"] = key_phrases
                    update = True
                
                if len(index["people"]) == 0 and len(index["organizations"]) == 0 and len(index["locations"]) == 0:
                    entities = textanalytics_connector.entity_recognition(messages=[chunk],language=index["language"])
                    index["people"] = entities[tak.PERSON.value]
                    index["organizations"] = entities[tak.ORGANIZATION.value]
                    index["locations"] = entities[tak.LOCATION.value]
                    index["dateTime"] = [parser.parse(date).replace(microsecond=0).isoformat() + "Z" if is_valid_date(date) else date for date in entities[tak.DATETIME.value] ]
                    update = True
                    
                if update:
                    update_index(index_name=index_name, data=results["rs"])
                    await add_skills_to_knowledge_db(index)
            
            docs += 1
            print(f"{docs}/{len(results['rs'])}...")            
        end_time = time.time()
        print(f"Total time: {end_time - start_time:.5f} sec")
    except Exception as e:
        update_index(index_name=index_name, data=results["rs"])
        end_time = time.time()
        print(f"Total time: {end_time - start_time:.5f} sec")
        print(f"Error While Applying Skills: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while monitoring indexer: {str(e)}")     
            
def is_valid_date(date_str):
    try:
        parser.parse(date_str)
        return True
    except ValueError:
        return False

def get_crawling_status():
    try:
        entity_settings = settings_service.get_settings_by_entity(config.ENTITY_NAME)[0]
        media_settings = entity_settings.get("media_settings", None)
        urls = media_settings.get("crawling_urls", [])
        return urls
    except Exception as e:
        raise Exception(f"{str(e)}")

async def add_skills_to_knowledge_db(entity: dict):
    try:
        entity_copy = copy.deepcopy(entity)  # Create an independent copy

        # Remove unnecessary fields
        for key in ["text_vector", "@search.score", "@search.reranker_score", "@search.highlights", "@search.captions"]:
            entity_copy.pop(key, None)

        entity_copy["PartitionKey"] = str(uuid.uuid4())
        entity_copy["RowKey"] = str(uuid.uuid4())

        # Convert list fields to strings, replace empty lists with None
        for key in ["keyphrases", "people", "organizations", "locations", "dateTime"]:
            if isinstance(entity_copy.get(key), list):  # Check if it's a list
                entity_copy[key] = None if not entity_copy[key] else ",".join(map(str, entity_copy[key]))

        # Store the modified copy in the database
        await db_connector.add_entity(table_name=config.COSMOS_MEDIA_KNOWLEDGE_TABLE, entity=entity_copy)

    except Exception as e:
        print(f'{str(e)}')
        return Exception(f'{str(e)}')
    
def return_most_indexed_urls(from_date: str = None, to_date: str = None):
    try:
        filter_exp = " and ".join(filter(None, [f"IndexDate ge '{from_date}'" if from_date and validation_service.is_valid_utc_date(from_date) else None, f"IndexDate le '{to_date}'" if to_date and validation_service.is_valid_utc_date(to_date) else None]))
        return db_connector.get_entities(table_name=config.MOST_INDEXED_URLS_TABLE, filter_expression=filter_exp)
    except Exception as e:
        raise Exception(str(e))

def return_most_used_keywords(from_date: str = None, to_date: str = None):
    try:
        filter_exp = " and ".join(filter(None, [f"IndexDate ge '{from_date}'" if from_date and validation_service.is_valid_utc_date(from_date) else None, f"IndexDate le '{to_date}'" if to_date and validation_service.is_valid_utc_date(to_date) else None]))
        return db_connector.get_entities(table_name=config.MOST_USED_KEYWORDS_TABLE, filter_expression=filter_exp)
    except Exception as e:
        raise Exception(str(e))
