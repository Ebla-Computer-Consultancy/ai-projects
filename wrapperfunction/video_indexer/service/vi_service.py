import json
from typing import Dict
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
from azure.identity import ClientSecretCredential

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
        accessToken = get_access_token()["data"]
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
        print(get_access_token()["data"])
        params = {
          
          "accessToken":get_access_token()["data"]
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

    try:
    # Authenticate with Azure AD
        credential = ClientSecretCredential(tenant_id=config.TENANT_ID, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET_VALUE)
        token = credential.get_token("https://management.azure.com/.default").token

        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
def get_access_token() -> Dict:
    try:
        # Define the URL for generating the access token
        token = get_azure_token()
        url = "https://management.azure.com/subscriptions/fcd1f0ed-84c0-4a06-a4bd-a74a51026856/resourceGroups/RERA-RG-WE/providers/Microsoft.VideoIndexer/accounts/rerawe-vi-01/generateAccessToken?api-version=2024-01-01"

        # Prepare headers and body as per the Microsoft API documentation
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            
        }
        body = {
            "permissionType": "Contributor",
            "scope": "Account",
        }

        # Make the POST request to the API
        response = requests.post(url=url, headers=headers, json=body)
        print(response)

        # Raise an exception if the response status code indicates an error
        response.raise_for_status()

        # Parse the JSON response to extract the access token
        access_token = response.json().get("accessToken")

        # Return the result in a standard format
        return {
            "status": "SUCCESS",
            "message": "Access token generated successfully",
            "data": access_token,
        }
    except requests.RequestException as e:
        # Extract the status code and error details for the exception
        status_code = e.response.status_code if e.response else 500
        detail = e.response.json() if e.response else str(e)

        # Raise an HTTPException with detailed error information
        raise HTTPException(
            status_code=status_code,
            detail={
                "error": "Failed to generate Video Indexer token",
                "details": detail,
            },
        )

async def upload_video(video_file: UploadFile, request: Request):
    try:
        # Define the URL and headers for Video Indexer API
        url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos"
        headers = {
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY,
        }

        access_token = get_access_token()["data"]

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
 