
from wrapperfunction.core import config
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException
from azure.ai.textanalytics import TextAnalyticsClient
from wrapperfunction.admin.model.textanalytics_model import TextAnalyticsCatigories, TextAnalyticsKEYS as tak

text_analytics_client = TextAnalyticsClient(endpoint=config.AZURE_TEXT_ANALYTICS_ENDPOINT, credential=AzureKeyCredential(config.AZURE_TEXT_ANALYTICS_KEY))
def analyze_sentiment(messages: list):
    try:
        detected_language_response = text_analytics_client.detect_language(messages)
        language_code = detected_language_response[0].primary_language.iso6391_name

        language = "ar" if language_code == "(Unknown)" else language_code
        sentiment_response = text_analytics_client.analyze_sentiment(messages, language=language)[0]    


        return sentiment_response.sentiment  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in sentiment analysis: {str(e)}")

def detect_language(messages: list):
    try:
        detect_language_response = text_analytics_client.detect_language(documents = messages)[0]
        return {
            tak.LANGUAGE_NAME.value:detect_language_response.primary_language.name,
            tak.LANGUAGE_ISO6391_NAME.value:detect_language_response.primary_language.iso6391_name
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
        
        results = TextAnalyticsCatigories(
            organization=[entity.text for entity in recognize_entities.entities if entity.category == tak.ORGANIZATION.value],
            dateTime=[entity.text for entity in recognize_entities.entities if entity.category == tak.DATETIME.value],
            IPAddress=[entity.text for entity in recognize_entities.entities if entity.category == tak.IPADDRESS.value],
            person=[entity.text for entity in recognize_entities.entities if entity.category == tak.PERSON.value],
            personType=[entity.text for entity in recognize_entities.entities if entity.category == tak.PERSONTYPE.value],
            url=[entity.text for entity in recognize_entities.entities if entity.category == tak.URL.value],
            event=[entity.text for entity in recognize_entities.entities if entity.category == tak.EVENT.value],
            email=[entity.text for entity in recognize_entities.entities if entity.category == tak.EMAIL.value],
            location=[entity.text for entity in recognize_entities.entities if entity.category == tak.LOCATION.value],
            phoneNumber=[entity.text for entity in recognize_entities.entities if entity.category == tak.PHONENUMBER.value],
            skill=[entity.text for entity in recognize_entities.entities if entity.category == tak.SKILL.value],
            product=[entity.text for entity in recognize_entities.entities if entity.category == tak.PRODUCT.value],
            quantity=[entity.text for entity in recognize_entities.entities if entity.category == tak.QUANTITY.value],
            address=[entity.text for entity in recognize_entities.entities if entity.category == tak.ADDRESS.value],
            entities=recognize_entities.entities,)
        
        return results.to_dict()

        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in entity_recognition analysis: {str(e)}")  



