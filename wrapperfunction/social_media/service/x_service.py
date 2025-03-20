import datetime
import json
from typing import List
import uuid
from fastapi import HTTPException
from wrapperfunction.admin.integration import textanalytics_connector
from wrapperfunction.admin.model.textanalytics_model import TextAnalyticsKEYS as tak
from wrapperfunction.admin.service import blob_service
from wrapperfunction.chat_history.integration import cosmos_db_connector
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.function_auth.service import auth_service
from wrapperfunction.social_media.integration import x_connector
from wrapperfunction.social_media.model.x_model import XSearch

async def x_multi_search(data: List[XSearch]):
    try:
        for node in data:
            results = x_connector.x_search(query=node.query,
                    start_time=node.start_time,
                    end_time=node.end_time,
                    max_results=node.max_results)
            if results["meta"]["result_count"] > 0:
                prepare_x_data_and_upload(results)
                await add_x_data_to_knowledge_db(results)
        return ServiceReturn(
            status=StatusCode.SUCCESS,
            message=f"X Crawled Successfully",
            data=results
        ).to_dict()
    except Exception as e:
        raise Exception(str(e))

def prepare_x_data_and_upload(results: dict):
    try:
        tweets = results["includes"]["tweets"]
        index = 0
        media_info = config.get_media_info()
        for tweet in tweets:
            url = tweet["entities"].get("urls",[])
            page = {
                "content": tweet["text"],
                "url": url[0]["url"] if len(url) > 0 else None,
                "created_at": tweet["created_at"]
            }
            blob_service.append_blob(blob=json.dumps(page,ensure_ascii=False),blob_name=f"{index}_tweet.json",folder_name=f"social_media/X/{datetime.datetime.now().date()}",container_name=media_info.container_name,metadata_2=page["url"])
            index += 1
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error While Uploading X data: index-{index}:{str(e)}")

async def add_x_data_to_knowledge_db(results: dict):
    all_tweets = cosmos_db_connector.get_entities(config.X_TABLE)
    existing_tweet_ids = {tweet["tweet_id"] for tweet in all_tweets} # Convert to set for faster searching
    
    data = results["data"]
    for tweet in data:
        if tweet["id"] not in existing_tweet_ids:
            tweet_data = get_author_data(tweet["author_id"], results)
            tweet_data["text"] = tweet["text"]
            tweet_data["created_at"] = tweet["created_at"]
            tweet_data["tweet_id"] = tweet["id"]
            tweet_data["PartitionKey"] = str(uuid.uuid4())
            tweet_data["RowKey"] = str(uuid.uuid4())
            tweet_data["language"] = textanalytics_connector.detect_language(messages=[tweet["text"]])[tak.LANGUAGE_ISO6391_NAME.value]
            tweet_data["keyphrases"] = textanalytics_connector.extract_key_phrases(messages=[tweet["text"]],language=tweet_data["language"])
            tweet_data["keyphrases"] = None if len(tweet_data["keyphrases"]) == 0 else ",".join(map(str, tweet_data["keyphrases"]))
            tweet_data["sentiment"] = textanalytics_connector.analyze_sentiment(messages=[tweet["text"]])
            if auth_service.exist_property(dic=tweet, field="referenced_tweets"):
                tweet_data["referenced_tweets"] = get_ids_list(tweet["referenced_tweets"])
            await cosmos_db_connector.add_entity(config.X_TABLE,tweet_data)

def get_author_data(id: str, results: dict) -> dict:
    users = results["includes"]["users"]
    for user in users:
        if user["id"] == id:
            return {
                "profile_created_at": user["created_at"],
                "name": user["name"],
                "username": user["username"],
                "user_id": user["id"],
                "verified": user["verified"],
                "profile_image_url": user["profile_image_url"]
            }
    return {}

def get_ids_list(nodes_list: list):
    ids_list = []
    for node in nodes_list:
        ids_list.append(node["id"])
    return ",".join(map(str, ids_list))         