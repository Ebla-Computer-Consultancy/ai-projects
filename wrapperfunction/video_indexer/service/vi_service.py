import json
import uuid
import requests
import httpx
from typing import Dict
from fastapi import HTTPException, UploadFile
from azure.identity import ClientSecretCredential
from wrapperfunction.chatbot.integration import openai_connector
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode

async def create_video_index(v_name: str, v_url: str):
    try:
        base_url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}"
        url = f"{base_url}/Videos"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY,
        }

        access_token = get_access_token()["data"]
        params = {
            "name": v_name,
            "privacy": "Public",
            "language": "auto",
            "videoUrl": v_url,
            "accessToken": access_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                video_url = v_url

                if not video_url:
                    raise HTTPException(status_code=500, detail="Failed to retrieve video URL.")

                return {
                    "status": "SUCCESS",
                    "message": f"{v_name} indexing has started successfully.",
                    "data": {"video_url": video_url, "video_details": data},
                }

            else:
                raise HTTPException(
                    status_code=response.status_code, detail=response.json()
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def get_azure_token() -> str:

    try:
    # Authenticate with Azure AD
        credential = ClientSecretCredential(tenant_id=config.TENANT_ID, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET_VALUE)
        token = credential.get_token("https://management.azure.com/.default").token

        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
def get_access_token() -> Dict:
    try:
        token = get_azure_token()
        url = f"https://management.azure.com/subscriptions/{config.SUBSCRIPTION_ID}/resourceGroups/{config.RESOURCE_GROUP_NAME}/providers/Microsoft.VideoIndexer/accounts/{config.ACCOUNT_NAME}/generateAccessToken?api-version={config.API_VERSION}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",           
        }
        body = {
            "permissionType": "Contributor",
            "scope": "Account",
        }


        response = requests.post(url=url, headers=headers, json=body)

        response.raise_for_status()


        access_token = response.json().get("accessToken")


        return {
            "status": "SUCCESS",
            "message": "Access token generated successfully",
            "data": access_token,
        }
    except requests.RequestException as e:

        status_code = e.response.status_code if e.response else 500
        detail = e.response.json() if e.response else str(e)


        raise HTTPException(
            status_code=status_code,
            detail={
                "error": "Failed to generate Video Indexer token",
                "details": detail,
            },
        )

async def get_video_index(video_id: str,bot_name: str):
    try:
        access_token = get_access_token()["data"]
        status_url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Index"
        params = {"accessToken": access_token}

        async with httpx.AsyncClient() as client:
            response = await client.get(url=status_url, params=params)
            if response.status_code == 200:
                res_data = response.json()


                if res_data.get("state") == "Processed":
                    await add_thumbnail_urls(res_data, access_token, video_id)
                    transcript = " ".join(entry["text"] for entry in res_data.get("videos", [{}])[0].get("insights", {}).get("transcript", []))
                    summary_content = f"Transcript: {transcript}"

                    summary = summarize_with_openai(summary_content.strip(),bot_name)
                    return ServiceReturn(
                        status=StatusCode.SUCCESS,
                        message=f"Indexing completed successfully for video ID: {video_id}",
                        data={"res_data": res_data,"summary": summary}
                    ).to_dict()

                elif res_data.get("state") == "Failed":
                    return ServiceReturn(
                        status=StatusCode.BAD_REQUEST,
                        message=f"Indexing failed for video ID: {video_id}",
                        data=res_data
                    ).to_dict()

                else:
                    return ServiceReturn(
                        status=StatusCode.PENDING,
                        message=f"Indexing in progress for video ID: {video_id}",
                        data=res_data
                    ).to_dict()

            else:
                raise HTTPException(status_code=500, detail="Failed to fetch indexing status")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def add_thumbnail_urls(res_data, access_token, video_id):
    base_url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Thumbnails/"
    
    thumbnail_id = res_data.get("summarizedInsights", {}).get("thumbnailId")
    if thumbnail_id:
        res_data["summarizedInsights"]["thumbnail_url"] = f"{base_url}{thumbnail_id}?accessToken={access_token}"

    for face in res_data.get("summarizedInsights", {}).get("faces", []):
        if face_thumbnail_id := face.get("thumbnailId"):
            face["thumbnail_url"] = f"{base_url}{face_thumbnail_id}?accessToken={access_token}"

    for video in res_data.get("videos", []):
        video_thumbnail_id = video.get("thumbnailId")
        if video_thumbnail_id:
            video["thumbnail_url"] = f"{base_url}{video_thumbnail_id}?accessToken={access_token}"

        for insight in video.get("insights", {}).get("faces", []):
            insight_thumbnail_id = insight.get("thumbnailId")
            if insight_thumbnail_id:
                insight["thumbnail_url"] = f"{base_url}{insight_thumbnail_id}?accessToken={access_token}"

        for label in video.get("insights", {}).get("labels", []):
            label_thumbnail_id = label.get("thumbnailId")
            if label_thumbnail_id:
                label["thumbnail_url"] = f"{base_url}{label_thumbnail_id}?accessToken={access_token}"

        for scene in video.get("insights", {}).get("scenes", []):
            scene_thumbnail_id = scene.get("thumbnailId")
            if scene_thumbnail_id:
                scene["thumbnail_url"] = f"{base_url}{scene_thumbnail_id}?accessToken={access_token}"

        for shot in video.get("insights", {}).get("shots", []):
            shot_thumbnail_id = shot.get("thumbnailId")
            if shot_thumbnail_id:
                shot["thumbnail_url"] = f"{base_url}{shot_thumbnail_id}?accessToken={access_token}"

            for key_frame in shot.get("keyFrames", []):
                key_frame_thumbnail_id = key_frame.get("instances", [{}])[0].get("thumbnailId")
                if key_frame_thumbnail_id:
                    key_frame["thumbnail_url"] = f"{base_url}{key_frame_thumbnail_id}?accessToken={access_token}"

def summarize_with_openai(content: str,bot_name: str):
    try:
        response = openai_connector.chat_completion(
            chatbot_setting=config.load_chatbot_settings(bot_name),
            chat_history=[{"role": "system", "content": "Summarize the content."}, {"role": "user", "content": content}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"Error summarizing content: {str(e)}"
    
async def upload_video(video_file: UploadFile):
    try:
        url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos"
        headers = {
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY,
        }

        access_token = get_access_token()["data"]

        params = {
            "accessToken": access_token,
            "name": video_file.filename,
            "privacy": "Public",
            "language": "auto"
        }

        video_content = await video_file.read()

        files = {
            "file": (video_file.filename, video_content, video_file.content_type),
        }

        response = requests.post(url, headers=headers, params=params, files=files)

        if response.status_code == 200:
            data = response.json()
            video_id = data.get("id")
            video_url = f"https://www.videoindexer.ai/accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/videos/{video_id}"

            return ServiceReturn(
                status=StatusCode.SUCCESS,
                message="Video uploaded successfully. Indexing in progress.",
                data={
                    "video_id": video_id,
                    "video_url": video_url
                }
            ).to_dict()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def reindex_video(v_id: str):
    try:
        url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{v_id}/ReIndex"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY
        }
        accessToken = get_access_token()["data"]
        params = {
          "accessToken": accessToken["data"]["accessToken"]
        }
        res = requests.put(url=url, headers=headers, params=params)
        if res.ok:
            return ServiceReturn(
                status=StatusCode.SUCCESS,
                message=f"{v_id} Is ReIndexed Successfully", 
                data=res
            ).to_dict()
        else:
            raise HTTPException(status_code=500, detail=json.loads(res.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_all_videos():
    try:
        url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY
        }

        access_token = get_access_token()["data"]
        params = {"accessToken": access_token}

        res = requests.get(url=url, headers=headers, params=params)
        if res.ok:
            res_data = json.loads(res.content)

            videos = []
            for v in res_data["results"]:
                video_id = v["id"]
                video_name = v["name"]
                thumbnail_url = get_video_thumbnail(video_id, access_token)
                videos.append({"name": video_name, "id": video_id, "thumbnail_url": thumbnail_url})

            return {
                "status": "SUCCESS",
                "message": "Videos retrieved successfully",
                "data": {"videos": videos}
            }
        else:
            raise HTTPException(status_code=500, detail=res.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def get_video_thumbnail(video_id, access_token):
    try:
        metadata_url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Index"
        params = {"accessToken": access_token}
        res = requests.get(metadata_url, params=params)

        if res.ok:
            metadata = res.json()
            thumbnail_id = metadata.get("summarizedInsights", {}).get("thumbnailId")

            if thumbnail_id:
                return f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Thumbnails/{thumbnail_id}?accessToken={access_token}"
            else:
                return None
        else:
            return None

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
