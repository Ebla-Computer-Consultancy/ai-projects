from fastapi import HTTPException
import requests
import datetime
from wrapperfunction.core import config

def x_search(query: str, start_time: str = None, end_time: str = None, max_results: int = None):
    try:
        url = "https://api.x.com/2/tweets/search/recent"

        querystring = {
            "query": query,
            "start_time": start_time if start_time else datetime.datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_time": end_time,
            "max_results": max_results if 10 <= max_results <= 100 else 100,
            "user.fields": "name,entities,profile_banner_url,profile_image_url,username,verified,created_at",
            "tweet.fields": "entities,text,referenced_tweets,created_at",
            "place.fields": "country,full_name,geo,name",
            "media.fields": "alt_text,url,type",
            "expansions": "author_id,referenced_tweets.id,entities.mentions.username,geo.place_id,attachments.media_keys"
        }

        headers = {"Authorization": f"Bearer {config.X_KEY}"}

        response = requests.get(url, headers=headers, params=querystring)

        if not response.ok:
            raise Exception(response.content)

        results = response.json()
        result_count = results.get("meta", {}).get("result_count", 0)
        next_token = results.get("meta", {}).get("next_token")

        # Initialize 'includes' if missing
        results.setdefault("includes", {})

        # If max_results > 100, paginate
        while next_token and result_count < max_results:
            querystring["next_token"] = next_token
            querystring["max_results"] = min(100, max_results - result_count)

            response = requests.get(url, headers=headers, params=querystring)
            if not response.ok:
                break

            res = response.json()
            results["data"].extend(res.get("data", []))  # Append new tweets

            # Merge includes (users, media, places, etc.)
            for key in res.get("includes", {}):
                results["includes"].setdefault(key, []).extend(res["includes"].get(key, []))

            # Update pagination metadata
            result_count += res.get("meta", {}).get("result_count", 0)
            results["meta"]["result_count"] = result_count
            next_token = res.get("meta", {}).get("next_token")

        return results

    except Exception as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))
