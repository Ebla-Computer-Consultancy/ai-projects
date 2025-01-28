import json
import uuid
from fastapi import HTTPException,Request,UploadFile
import httpx
import requests
import requests.auth
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity
from wrapperfunction.chat_history.model.message_entity import MessageEntity, MessageType, Roles
from wrapperfunction.chat_history.service.chat_history_service import add_entity
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode

import httpx
import asyncio
from fastapi import HTTPException

from wrapperfunction.core.utls.helper import extract_client_details

async def create_video_index(v_name: str, v_url: str,request: Request):
    try:
        base_url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}"
        url = f"{base_url}/Videos"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY,
        }

        params = {
            "name": v_name,
            "privacy": "Public",
            "language": "auto",
            "videoUrl": v_url,
            "accessToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJWZXJzaW9uIjoiMi4wLjAuMCIsIktleVZlcnNpb24iOiIxNGIwZDg4NTU0OTE0YjkwYjBkYjEwM2M0NmRkYTNkNiIsIkFjY291bnRJZCI6ImE2ZmRiZWNmLTAxMDEtNDEzYy1iMjA4LTk5ZTg5ZjRjOWI3NyIsIkFjY291bnRUeXBlIjoiQXJtIiwiUGVybWlzc2lvbiI6IkNvbnRyaWJ1dG9yIiwiRXh0ZXJuYWxVc2VySWQiOiJGMjhBRUM0REM1NDA0Q0IwQkY3Q0UxOEQ5MUY1REUzMSIsIlVzZXJUeXBlIjoiTWljcm9zb2Z0Q29ycEFhZCIsIklzc3VlckxvY2F0aW9uIjoid2VzdGV1cm9wZSIsIm5iZiI6MTczODA1ODE0NywiZXhwIjoxNzM4MDYyMDQ3LCJpc3MiOiJodHRwczovL2FwaS52aWRlb2luZGV4ZXIuYWkvIiwiYXVkIjoiaHR0cHM6Ly9hcGkudmlkZW9pbmRleGVyLmFpLyJ9.fOaZOuQdqYzi8Ckq1gb1mX35fW1WOn7dGNcLufd_5NY8iv1zATACwuK6_-O-QXM_QUuo_Re475v2l2X1DqyAFj9Tc2ke4vrR9q1o9r6CNUiQQpzWMyb295W9MtE9I7Tqq10eyDah189moMPA29vj-8aJT8LCzLqzfmSavYgtTIwk-WfD2fIaqR0XMJL8MfA-tmgSxxY_7sBnSR74WyY7CGwst-bz8nD4e8jHLAUEYY0T7vjgYMZtofZNE7sl5I5sDirlWlZZyNE7pOoX0wdJKtkpcY5zLfZOonL7r6O69qBuC_CDVE0LzNnyBnhi0VswVflDrK9NOceCAiC_MDe1Ug",  # Add your valid access token here
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                video_id = data.get("id")

                for _ in range(60): 
                    status_url = f"{base_url}/Videos/{video_id}/Index"
                    status_params = {"accessToken": params["accessToken"]}
                    status_response = await client.get(url=status_url, params=status_params)

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        indexing_state = status_data.get("state")

                        if indexing_state == "Processed":
                            client_details=extract_client_details(request)
                            conv_entity = ConversationEntity(
                                user_id=str(uuid.uuid4()),
                                conversation_id=video_id,
                                bot_name="video-indexer",
                                title=v_name,
                              client_ip=client_details["client_ip"],
                            forwarded_ip=client_details["forwarded_ip"],
                            device_info=json.dumps(client_details["device_info"]),
                            )

                            video_message = MessageEntity(
                                content=json.dumps(status_data),
                                conversation_id=video_id,
                                role=Roles.Assistant.value,
                                context="VideoIndexer",
                                type=MessageType.Video.value,
                            )

                            await add_entity(conv_entity=conv_entity, message_entity=video_message)

                            return {
                                "status": "SUCCESS",
                                "message": f"{v_name} Indexer has successfully completed processing.",
                                "data": status_data,
                            }
                        elif indexing_state in ["Failed", "Error"]:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Indexing failed with state: {indexing_state}",
                            )

                    await asyncio.sleep(10)

                raise HTTPException(
                    status_code=408,
                    detail="Indexing process timed out.",
                )

            else:
                raise HTTPException(
                    status_code=response.status_code, detail=response.json()
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



async def get_video_index(v_id: str):
    try:
        url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{v_id}/Index?accessToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJWZXJzaW9uIjoiMi4wLjAuMCIsIktleVZlcnNpb24iOiIxNGIwZDg4NTU0OTE0YjkwYjBkYjEwM2M0NmRkYTNkNiIsIkFjY291bnRJZCI6ImE2ZmRiZWNmLTAxMDEtNDEzYy1iMjA4LTk5ZTg5ZjRjOWI3NyIsIkFjY291bnRUeXBlIjoiQXJtIiwiUGVybWlzc2lvbiI6IkNvbnRyaWJ1dG9yIiwiRXh0ZXJuYWxVc2VySWQiOiJGMjhBRUM0REM1NDA0Q0IwQkY3Q0UxOEQ5MUY1REUzMSIsIlVzZXJUeXBlIjoiTWljcm9zb2Z0Q29ycEFhZCIsIklzc3VlckxvY2F0aW9uIjoid2VzdGV1cm9wZSIsIm5iZiI6MTczODA2MzEyNCwiZXhwIjoxNzM4MDY3MDI0LCJpc3MiOiJodHRwczovL2FwaS52aWRlb2luZGV4ZXIuYWkvIiwiYXVkIjoiaHR0cHM6Ly9hcGkudmlkZW9pbmRleGVyLmFpLyJ9.VARcCoiuqMdWOKipJ0_df3sMPTShWxKd2gNiys4vl5h9Lf7PjaLgNjBo7KezvbAhfoN3WhsXORO3vOvupfoZ5BZ-kJ594gcqwirctkX7zV3rBkPMZWZCrp5hVlc43OEx14Yt3S3uiU5P_Ns8MK4_h8VqDtFUpRapQPepzVMRNZUymwzu2DegUa8Hd7FnJOkOCg1rWi5F23ulYegr7rrD8hOXqXphNKRf2Tz4QNrOke2dfzrcQA-0lhB_fOFP1EjmPg_JA_KJ2JjH2g7QPN3dpRcSTxkcZYBe3q0OpjKhzoTK84zFZE-YvIeBhXfhBjqqkPosXHfJN-dPXtNbJYKidw"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY
        }
        
        res = requests.get(url=url,headers=headers)
        if res.ok:
          res = json.loads(res.content)
          return ServiceReturn(
                              status=StatusCode.SUCCESS,
                              message=f"{res['name']} Is Getten Successfuly", 
                              data=res
                              ).to_dict()
        else:
          raise HTTPException(status_code=500, detail=res.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def reindex_video(v_id: str):
    try:
        url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{v_id}/ReIndex"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY
        }
        accessToken = "get_AccessToken()"
        params = {
          "accessToken":accessToken["data"]["accessToken"]
        }
        res = requests.put(url=url,headers=headers,params=params)
        if res.ok:
          return ServiceReturn(
                              status=StatusCode.SUCCESS,
                              message=f"{v_id} Is ReIndexed Successfuly", 
                              data=res
                              ).to_dict()
        else:
          raise HTTPException(status_code=500, detail=json.loads(res.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_all_video():
    try:
        url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY
        }
        # accessToken = get_AccessToken()
        params = {
          
          "accessToken":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJWZXJzaW9uIjoiMi4wLjAuMCIsIktleVZlcnNpb24iOiIxNGIwZDg4NTU0OTE0YjkwYjBkYjEwM2M0NmRkYTNkNiIsIkFjY291bnRJZCI6ImE2ZmRiZWNmLTAxMDEtNDEzYy1iMjA4LTk5ZTg5ZjRjOWI3NyIsIkFjY291bnRUeXBlIjoiQXJtIiwiUGVybWlzc2lvbiI6IkNvbnRyaWJ1dG9yIiwiRXh0ZXJuYWxVc2VySWQiOiJGMjhBRUM0REM1NDA0Q0IwQkY3Q0UxOEQ5MUY1REUzMSIsIlVzZXJUeXBlIjoiTWljcm9zb2Z0Q29ycEFhZCIsIklzc3VlckxvY2F0aW9uIjoid2VzdGV1cm9wZSIsIm5iZiI6MTczODA1NTIyMCwiZXhwIjoxNzM4MDU5MTIwLCJpc3MiOiJodHRwczovL2FwaS52aWRlb2luZGV4ZXIuYWkvIiwiYXVkIjoiaHR0cHM6Ly9hcGkudmlkZW9pbmRleGVyLmFpLyJ9.lpUEVgyjgo0jZwA0SlpHI_hpIcn5aY3FOynydc6KDk1QjOXezKXljD19erC6hf1YoD5_g0WvR_bOzH62XazDI_qI2iTk5MtDkhhBlIuAwdEYh_K9nEPxHMsYxBpdFKkMyVfM5VY7thwvL-hIcBCqyrjwbErlQAPQWK8pWBjS7sB3K_Ce2zVFaCc1FUD43ab5Vfozy9GILPaWkO_J-2eSTMAQCXcvrl4zXwahy54LSWqgedC5Pnd05NbOvp2Jv4uoPG6CVFWLmBQbJSPbjAyeCbpE6EbDn0Y82g7v1EZh_7a6WcabVBSQ6a3fBQnzcokbBDSDZz6kgej3wMxKPX3R_Q"
        }
        res = requests.get(url=url,headers=headers,params=params)
        if res.ok:
          res = json.loads(res.content)
          return ServiceReturn(
                              status=StatusCode.SUCCESS,
                              message=f"Videos Is Getten Successfuly", 
                              data={"videos_id":[{"name":v["name"],"id":v["id"]} for v in res["results"]],
                                    "videos_data": res["results"]}
                              ).to_dict()
        else:
          raise HTTPException(status_code=500, detail=res.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_azure_token() -> str:
    url = f"https://login.microsoftonline.com/{config.TENANT_ID}/oauth2/v2.0/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET_VALUE,
        "scope": "https://management.azure.com/.default",
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response else 500
        detail = e.response.content.decode("utf-8") if e.response else str(e)
        raise HTTPException(
            status_code=status_code,
            detail=f"Failed to get token: {detail}",
        )

# Function to get Video Indexer Access Token
# def get_access_token() -> ServiceReturn:
#     try:
#         # Get Azure Bearer Token
#         token = get_azure_token()
#         url = f"https://management.azure.com/subscriptions/fcd1f0ed-84c0-4a06-a4bd-a74a51026856/resourceGroups/RERA-RG-WE/providers/Microsoft.VideoIndexer/accounts/rerawe-vi-01/generateAccessToken?api-version=2024-01-01"

#         headers = {
#             "Authorization": f"Bearer {token",
#             "Content-Type": "application/json",
#             "Ocp-Apim-Subscription-Key": f"{config.VIDEO_INDEXER_ACCOUNT_ID}",
#         }

#         response = requests.post(url=url, headers=headers)
#         response.raise_for_status()
#         access_token = response.json().get("accessToken")

#         return ServiceReturn(
#             status=StatusCode.SUCCESS,
#             message="Access token generated successfully",
#             data=access_token,
#         ).to_dict()
#     except requests.RequestException as e:
#         status_code = e.response.status_code if e.response else 500
#         detail = e.response.content.decode("utf-8") if e.response else str(e)
#         raise HTTPException(
#             status_code=status_code,
#             detail=f"Failed to generate Video Indexer token: {detail}",
#         )

async def upload_video(video_file: UploadFile, request: Request):
    try:
        # Define the URL and headers for Video Indexer API
        url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos"
        headers = {
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY,
        }

        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IllUY2VPNUlKeXlxUjZqekRTNWlBYnBlNDJKdyIsImtpZCI6IllUY2VPNUlKeXlxUjZqekRTNWlBYnBlNDJKdyJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuYXp1cmUuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvOTkxNjkxYTItZGRmYS00ZDRiLTk5ZWEtMzc3OWI2MzRhNDMwLyIsImlhdCI6MTczODA3ODE1NiwibmJmIjoxNzM4MDc4MTU2LCJleHAiOjE3MzgwODIwNTYsImFpbyI6ImsyUmdZTmc2MCt2YzNLaXdXZWVZSndycEhWc2tEZ0E9IiwiYXBwaWQiOiJiMjFmYjFmYS02ZDJmLTRmYzktYmVmNS04ZjZhZTAwYTg1NTIiLCJhcHBpZGFjciI6IjEiLCJpZHAiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC85OTE2OTFhMi1kZGZhLTRkNGItOTllYS0zNzc5YjYzNGE0MzAvIiwiaWR0eXAiOiJhcHAiLCJvaWQiOiJjNTcwMTIwNy1kYWMxLTRhYTgtYmFiYi1iZjE4YTc4NTJkZmYiLCJyaCI6IjEuQVVnQW9wRVdtZnJkUzAyWjZqZDV0alNrTUVaSWYza0F1dGRQdWtQYXdmajJNQk1MQVFCSUFBLiIsInN1YiI6ImM1NzAxMjA3LWRhYzEtNGFhOC1iYWJiLWJmMThhNzg1MmRmZiIsInRpZCI6Ijk5MTY5MWEyLWRkZmEtNGQ0Yi05OWVhLTM3NzliNjM0YTQzMCIsInV0aSI6Ii1JSm55YlRUNTBLZ0dGdHdYSmxVQUEiLCJ2ZXIiOiIxLjAiLCJ4bXNfaWRyZWwiOiI3IDMwIiwieG1zX3RjZHQiOjE1ODM4MzcyOTJ9.KUEKI7-QQDK_CC5LDQwU8CQEbDkQPnjME9ZLF2dxgXC6EkVhLldU8881ugKmeuNv8H4KrBW375YIWv49CsS6dZiapWiO4FDT2STwawfH8WpI77n4cJDz0jSMlioe4gIe7SwSlRKrLqhlivsZyiVsOdJYkBMZoyHpoq5qLrhuO_HUq4MVAwo1QjcTZehfvYQ9iOs7uTgSSg_u1bemOdCTSOW_E0Kn09WmIroBsuH2AMttAvtDTZ0K0012PJ72CbNZWfQFX4BUERrIGonGpALJarzmzMNZ8QdV6qkYe4vDv_DVgSuVDc2yvFuRGu_o7Z_gbQ6zC8JebwFQ_sX0WvrCMw"

        # Prepare the query parameters
        params = {
            "accessToken": access_token,
            "name": video_file.filename,
            "privacy": "Public",
            "language": "auto"
        }

        # Read the video file in binary mode
        video_content = await video_file.read()

        # Prepare the multipart request
        files = {
            "file": (video_file.filename, video_content, video_file.content_type),
        }

        # Make the POST request to upload the video
        response = requests.post(url, headers=headers, params=params, files=files)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            video_id = data.get("id")

            # Polling for indexing status
            status_url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Index"
            status_params = {"accessToken": access_token}

            while True:
                status_response = requests.get(status_url, headers=headers, params=status_params)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    indexing_state = status_data.get("state")

                    if indexing_state == "Processed":
                        client_details = extract_client_details(request)

                        conv_entity = ConversationEntity(
                user_id=str(uuid.uuid4()),
            conversation_id=video_id,
            bot_name="video-indexer",
            title="",
            client_ip=client_details["client_ip"],
            forwarded_ip=client_details["forwarded_ip"],
            device_info=json.dumps(client_details["device_info"]),
        )
                        message_entity = MessageEntity(
            content=status_data,
            conversation_id=video_id,
            role=Roles.User.value,
            context="",
            type=MessageType.Video.value,
        )


                        await add_entity(message_entity=message_entity, conv_entity=conv_entity)
                        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            message=f"Video '{video_file.filename}' uploaded and indexed successfully.",
                            data={"video_id": video_id, "details": status_data}
                        ).to_dict()
                    elif indexing_state in ["Failed", "Error"]:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Video indexing failed: {indexing_state}"
                        )
                else:
                    raise HTTPException(
                        status_code=status_response.status_code,
                        detail=status_response.json()
                    )
                await asyncio.sleep(10)
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 