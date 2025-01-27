import json
from fastapi import HTTPException
import requests
import requests.auth
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode

async def create_video_index(v_name:str, v_url):
    try:
        url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.VIDEO_INDEXER_KEY
        }
        accessToken = get_AccessToken()
        params = {
          "name": v_name,
          "privacy": "Public",
          "language": "auto",
          "videoUrl": v_url,
          "accessToken":accessToken["data"]["accessToken"]
        }
        res = requests.post(url=url,headers=headers,params=params)

        if res.ok:
          return ServiceReturn(
                              status=StatusCode.SUCCESS,
                              message=f"{v_name} Indexer Is Created and now Running Successfuly", 
                              data=json.loads(res.connection)
                              ).to_dict()
        else:
          raise HTTPException(status_code=500, detail=res.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_video_index(v_id: str):
    try:
        url = f"https://api.videoindexer.ai/westeurope/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{v_id}/Index"
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
        accessToken = get_AccessToken()
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
        accessToken = get_AccessToken()
        params = {
          
          "accessToken":accessToken["data"]["accessToken"]
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


def get_AccessToken() -> ServiceReturn:
    try: 
        token = '''eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Inp4ZWcyV09OcFRrd041R21lWWN1VGR0QzZKMCIsImtpZCI6Inp4ZWcyV09OcFRrd041R21lWWN1VGR0QzZKMCJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuYXp1cmUuY29tLyIsImlzcyI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0Lzk5MTY5MWEyLWRkZmEtNGQ0Yi05OWVhLTM3NzliNjM0YTQzMC8iLCJpYXQiOjE3MzMwNTI0MTksIm5iZiI6MTczMzA1MjQxOSwiZXhwIjoxNzMzMDU3Mzc4LCJhY3IiOiIxIiwiYWlvIjoiQVZRQXEvOFlBQUFBd09DYkhsN3E3M21nY003T2hhelVrYUxJOTN4WS9BT0dVVnZrVzVFYUx3YnN5QmdkNXpCQVFELzA4YkxNRFo0U0lEQ25FR1BHVGtCRCtPcnZhZEIwdjJPanRqYm5YSnplbG1lN2ZLSE5zTVE9IiwiYW1yIjpbInB3ZCIsIm1mYSJdLCJhcHBpZCI6IjA0YjA3Nzk1LThkZGItNDYxYS1iYmVlLTAyZjllMWJmN2I0NiIsImFwcGlkYWNyIjoiMCIsImZhbWlseV9uYW1lIjoiUWFyYXdpIiwiZ2l2ZW5fbmFtZSI6IkFzaW0iLCJncm91cHMiOlsiNjEwZTM4NTUtZmY5YS00MDhkLTljZGMtYzRjNDRiMjNkZDE2Il0sImlkdHlwIjoidXNlciIsImlwYWRkciI6IjM3LjE4Ni41NS4yNDciLCJuYW1lIjoiQXNpbSBRYXJhd2kiLCJvaWQiOiJiZWUwMDQxYy0yNzc5LTQ4OGUtOGVhYy0xZWMyZTdmODg4MzIiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMjM4ODYxMDYzNC0xNjUwNzg4NjI4LTE5Njg1ODQyNjEtMTI3MjgiLCJwdWlkIjoiMTAwMzIwMDNEQjM2QkRCRCIsInB3ZF91cmwiOiJodHRwczovL3BvcnRhbC5taWNyb3NvZnRvbmxpbmUuY29tL0NoYW5nZVBhc3N3b3JkLmFzcHgiLCJyaCI6IjEuQVVnQW9wRVdtZnJkUzAyWjZqZDV0alNrTUVaSWYza0F1dGRQdWtQYXdmajJNQk1MQWFsSUFBLiIsInNjcCI6InVzZXJfaW1wZXJzb25hdGlvbiIsInN1YiI6IjBSdU9sanRtWTd1dWd1NjFtR05QSlk0MzVLanNiSnA5QXlYVlNETkRoME0iLCJ0aWQiOiI5OTE2OTFhMi1kZGZhLTRkNGItOTllYS0zNzc5YjYzNGE0MzAiLCJ1bmlxdWVfbmFtZSI6ImFxYXJhd2lAZWJsYWNvcnAuY29tIiwidXBuIjoiYXFhcmF3aUBlYmxhY29ycC5jb20iLCJ1dGkiOiJCUk9WNFVUYlcwVzZzN3JKVS1VdkFBIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXSwieG1zX2NhZSI6IjEiLCJ4bXNfY2MiOlsiQ1AxIl0sInhtc19maWx0ZXJfaW5kZXgiOlsiNzIiXSwieG1zX2lkcmVsIjoiMSAyNCIsInhtc19yZCI6IjAuNDJMbFlCUmk5QUFBIiwieG1zX3NzbSI6IjEiLCJ4bXNfdGNkdCI6MTU4MzgzNzI5Mn0.Qd2XlbcXxicyZ8yXpfgb6yAxj46f5JMn7bgJlfJ466s7TCF-YupwM4nCayVaBikjI7K3IVlICsL5rAsDTM56Uz9mK1C6YAjgNnf4BLjdXLSswDGKv_znxTDnbpSu75SBPcazIx2Bolol74DDqaxuAMO7LQpvcpeE3Rfmu3dtUU-aHwAhvWQ6bHEtNNYK1KvALGrAR_rkF3x-zfAX-kYw8OaOL6FTLZBcpJicN85Ey7kavkqpD3qi8Ajw2MI1Ca0hlyZJujE3bACSbDxM4K690mhbUQ9TgZOawAq9uzIf5UxKrT2dicBQioPrqSRJQBzmSfhb6e35wyuiCjgfAzM7rQ'''
        
        url = "https://management.azure.com/subscriptions/fcd1f0ed-84c0-4a06-a4bd-a74a51026856/resourceGroups/RERA-RG-WE/providers/Microsoft.VideoIndexer/accounts/rerawe-vi-01/generateAccessToken?api-version=2024-01-01"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        body = {
          "permissionType": "Contributor",
          "scope": "Account"
        }
        
        res = requests.post(url=url,headers=headers,json=body)
        if res.ok:
          res = json.loads(res.content)
          return ServiceReturn(
                              status=StatusCode.SUCCESS,
                              message=f"Videos Is Getten Successfuly", 
                              data=res
                              ).to_dict()
        else:
          raise HTTPException(status_code=500, detail=res.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))