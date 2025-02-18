import datetime
import json
import uuid
from fastapi import HTTPException
from wrapperfunction.admin.service import blob_service
from wrapperfunction.chat_history.integration import cosmos_db_connector
from wrapperfunction.core import config
from wrapperfunction.function_auth.service import auth_service


def prepare_x_data_and_upload(results: dict):
    try:
        tweets = results["includes"]["tweets"]
        index = 0
        for tweet in tweets:
            url = tweet["entities"].get("urls",[])
            page = {
                "content": tweet["text"],
                "url": url[0]["url"] if len(url) > 0 else None,
                "created_at": tweet["created_at"]
            }
            media_info = config.get_media_info()
            blob_service.append_blob(blob=json.dumps(page,ensure_ascii=False),blob_name=f"{index}_tweet.json",folder_name=f"social_media/X/{datetime.datetime.now().date()}",container_name=media_info["container_name"],metadata_2=page["url"])
            index += 1
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error While Uploading X data: index-{index}:{str(e)}")

async def add_x_data_to_knowledge_db(results: dict):
    data = results["data"]
    for tweet in data:
        tweet_data = get_author_data(tweet["author_id"], results)
        tweet_data["text"] = tweet["text"]
        tweet_data["created_at"] = tweet["created_at"]
        tweet_data["tweet_id"] = tweet["id"]
        tweet_data["PartitionKey"] = str(uuid.uuid4())
        tweet_data["RowKey"] = str(uuid.uuid4())
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