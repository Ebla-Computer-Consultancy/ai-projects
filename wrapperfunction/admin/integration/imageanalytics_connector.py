import requests
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException

from wrapperfunction.core import config

client = ImageAnalysisClient(
    endpoint=config.AZURE_IMAGE_ANALYTICS_ENDPOINT,
    credential=AzureKeyCredential(config.AZURE_IMAGE_ANALYTICS_KEY)
)

def analyze_image_from_url(img_url: str):
    try:
        result = client.analyze_from_url(
            image_url=img_url,
            visual_features=[
                VisualFeatures.CAPTION,
                VisualFeatures.READ,
                VisualFeatures.TAGS,
                VisualFeatures.SMART_CROPS,
                VisualFeatures.DENSE_CAPTIONS,
                VisualFeatures.PEOPLE
                ],
            gender_neutral_caption=False, 
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in Image analysis: {str(e)}")

def image_embedding(img_url: str):
    url = f"{config.AZURE_IMAGE_ANALYTICS_ENDPOINT}computervision/retrieval:vectorizeImage"
    params = {
        "api-version": config.OPENAI_API_VERSION,
        "model-version": config.OPENAI_API_MODEL_VERSION
    }
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": config.AZURE_IMAGE_ANALYTICS_KEY
    }
    payload = {
        "url": img_url
    }
    try:
        response = requests.post(url, params=params, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in Image Vectorize: {str(e)}")
