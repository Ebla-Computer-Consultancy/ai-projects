
from wrapperfunction.core import config
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException
from azure.ai.textanalytics import TextAnalyticsClient


text_analytics_client = TextAnalyticsClient(endpoint=config.AZURE_TEXT_ANALYTICS_ENDPOINT, credential=AzureKeyCredential(config.AZURE_TEXT_ANALYTICS_KEY))
def analyze_sentiment(messages: list):
    try:
        sentiment_response = text_analytics_client.analyze_sentiment(messages)[0]
        return sentiment_response.sentiment  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in sentiment analysis: {str(e)}")   

