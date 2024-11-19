
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

def detect_language(messages: list):
    try:
        detect_language_response = text_analytics_client.detect_language(documents = messages)[0]
        return {
            "name":detect_language_response.primary_language.name,
            "iso6391_name":detect_language_response.primary_language.iso6391_name
            }  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in detect_language analysis: {str(e)}")

def extract_key_phrases(messages: list, language: str):
    try:
        key_phrases_response = text_analytics_client.extract_key_phrases(documents = messages,language=language)[0]
        return key_phrases_response.key_phrases  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in key_phrases analysis: {str(e)}")

def entity_recognition(messages: list, language: str):
    try:
        recognize_entities = text_analytics_client.recognize_entities(documents = messages,language="en")[0]
        return {
                "Organization":[entity.text for entity in recognize_entities.entities if entity.category =="Organization"],
                "DateTime":[entity.text for entity in recognize_entities.entities if entity.category =="DateTime"],
                "IPAddress":[entity.text for entity in recognize_entities.entities if entity.category =="IPAddress"],
                "Person":[entity.text for entity in recognize_entities.entities if entity.category =="Person"],
                "PersonType":[entity.text for entity in recognize_entities.entities if entity.category =="PersonType"],
                "URL":[entity.text for entity in recognize_entities.entities if entity.category =="URL"],
                "Event":[entity.text for entity in recognize_entities.entities if entity.category =="Event"],
                "Email":[entity.text for entity in recognize_entities.entities if entity.category =="Email"],
                "Location":[entity.text for entity in recognize_entities.entities if entity.category =="Location"],
                "PhoneNumber":[entity.text for entity in recognize_entities.entities if entity.category =="PhoneNumber"],
                "Skill":[entity.text for entity in recognize_entities.entities if entity.category =="Skill"],
                "Product":[entity.text for entity in recognize_entities.entities if entity.category =="Product"],
                "Quantity":[entity.text for entity in recognize_entities.entities if entity.category =="Quantity"],
                "Address":[entity.text for entity in recognize_entities.entities if entity.category =="Address"],
                "entities":recognize_entities.entities
                }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in entity_recognition analysis: {str(e)}")  



