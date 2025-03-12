
import json
import requests
import httpx
from typing import Dict
from fastapi import HTTPException, UploadFile
from azure.identity import ClientSecretCredential
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

async def get_video_index(video_id: str,language:str):
    try:
        access_token = get_access_token()["data"]
        status_url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Index"
        params = {"accessToken": access_token,"language": language}

        async with httpx.AsyncClient() as client:
            response = await client.get(url=status_url, params=params)
            if response.status_code == 200:
                return  response.json()
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch indexing status")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def upload_video(video_file: UploadFile,language: str):
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
            "language": language
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
            return res_data
        else:
            raise HTTPException(status_code=500, detail=res.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def get_video_thumbnail(video_id):
    try:
        access_token = get_access_token()["data"]
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

async def get_stream_url(video_id: str):
    try:
        access_token = get_access_token()["data"]
        url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/streaming-url"
        params = {"accessToken": access_token}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return None

            data = response.json()
            manifest_url = data.get("url")
            if not manifest_url:
                return None

            manifest_response = await client.get(manifest_url)
            if manifest_response.status_code != 200:
                return None

            mpd_data = manifest_response.text.strip()
            return mpd_data
        return None
    except Exception:
        return None


    
async def get_video_download_url(video_id: str):
    try:
        access_token = get_access_token()["data"]
        url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/SourceFile/DownloadUrl"
        params = {"accessToken": access_token}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                return response.json() 

            return None
    except Exception:
        return None  

async def get_video_caption_url(video_id: str):
    try:
        access_token = get_access_token()["data"]
        url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Captions"

        return f"{url}?accessToken={access_token}&format=Vtt"
    except Exception:
        return None

def get_supported_languages():
    try:
        url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/SupportedLanguages"
        headers = {"Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return {"status": "success", "languages": response.json()}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))