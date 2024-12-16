from fastapi import HTTPException
from wrapperfunction.admin.integration import imageanalytics_connector
from wrapperfunction.admin.integration import textanalytics_connector
from wrapperfunction.admin.integration.blob_storage_integration import generate_blob_sas_url
from wrapperfunction.admin.model.crawl_model import CrawlRequestUrls
from wrapperfunction.admin.model.crawl_settings import CrawlSettings, IndexingType
from wrapperfunction.admin.service.blob_service import append_blob
from wrapperfunction.admin.service.crawl_service import crawl_urls
from wrapperfunction.chatbot.integration.openai_connector import  chat_completion
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.core.model import customskill_model
from wrapperfunction.core.model.customskill_model import CustomSkillReturnKeys as csrk
from wrapperfunction.admin.model.textanalytics_model import TextAnalyticsKEYS as tak
from wrapperfunction.core.utls.helper import clean_text

async def generate_report(search_text: str):
    try:
        user_message = f"write a long report in about 2 pages(reach the max)..about:{search_text}, note: add resources and dates",
        
        chat_settings = config.load_chatbot_settings(bot_name="media")
        chat_history = [{"role": "system", "content": chat_settings.system_message}]
        chat_history.append({"role": "user", "content": str(user_message)})

        chat_res = chat_completion(
            chatbot_setting=chat_settings,
            chat_history=chat_history
        )
        chat_res["message"]["content"] = clean_text(chat_res["message"]["content"]) 
        ref = {citation["url"] for citation in chat_res["message"]["context"]["citations"] if citation["url"] is not None}
        report_file_name = search_text.replace(" ","_")
        append_blob(blob=chat_res["message"]["content"],
                    metadata_3=IndexingType.GENERATED,
                    container_name= "rera-media-reports",
                    blob_name=f"{report_file_name}.txt")
        
        sas_url = generate_blob_sas_url(container_name= "rera-media-reports",
                                            blob_name=f"{report_file_name}.txt")
        # Push the file to the Azure container
        return ServiceReturn(
            status=StatusCode.CREATED,
            message=f"{search_text} Report Generated Successfully",
            data={
                "report_url": sas_url,
                "references":list(ref),
                "final_response": chat_res 
            }
        ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def media_crawl(urls: list[CrawlRequestUrls], settings: CrawlSettings):
    try:
        crawl_urls(
            urls,
            settings
        )
        
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            message=f"URL's:{urls} | Topics:{settings.topics} crawled successfully", 
                        ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def sentiment_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            text = record.data["text"]
            if not text:
                raise ValueError("Missing 'text' field in data")

            # Analyze sentiment
            sentiment = textanalytics_connector.analyze_sentiment([text])

            # Add successful result
            results.append(customskill_model.SkillRecord(
                    recordId=record_id,
                    data={
                            csrk.SENTIMENT.value: sentiment
                        },
                    errors=None,
                    warnings=None
                        ))
    
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(ve)}",
                warnings=None
            ))
        except Exception as e:
            # Catch unexpected errors
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(e)}",
                warnings=None
            ))
    return  customskill_model.CustomSkillReturn(values=results).to_dict()

async def detect_language_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            text = record.data["text"]
            if not text:
                raise ValueError("Missing 'text' field in data")

            # detect_language
            detected_language = textanalytics_connector.detect_language(messages=[text])

            # Add successful result
            results.append(customskill_model.SkillRecord(
                    recordId=record_id,
                    data={
                            tak.LANGUAGE_NAME.value: detected_language[tak.LANGUAGE_NAME.value],
                            tak.LANGUAGE_ISO6391_NAME.value: detected_language[tak.LANGUAGE_ISO6391_NAME.value]
                        },
                    errors=None,
                    warnings=None
                    ))
            
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(ve)}",
                warnings=None
            ))
        except Exception as e:
            # Catch unexpected errors
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(e)}",
                warnings=None
            ))
    return customskill_model.CustomSkillReturn(values=results).to_dict()
    
async def extract_key_phrases_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            text = record.data["text"]
            language = record.data["language"]
            if not text:
                raise ValueError("Missing 'text' field in data")

            # Analyze key_phrases
            key_phrases = textanalytics_connector.extract_key_phrases(messages=[text],language=language)

            # Add successful result
            results.append(
                customskill_model.SkillRecord(
                    recordId=record_id,
                    data=
                        {
                            csrk.KEYPHRASES.value: key_phrases
                        },
                    errors=None,
                    warnings=None
                        ))
            
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(ve)}",
                warnings=None
            ))
        except Exception as e:
            # Catch unexpected errors
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(e)}",
                warnings=None
            ))
    return customskill_model.CustomSkillReturn(values=results).to_dict()

async def entity_recognition_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            text = record.data["text"]
            language = record.data["language"]
            if not text:
                raise ValueError("Missing 'text' field in data")

            # Analyze entity_recognition
            entities = textanalytics_connector.entity_recognition(messages=[text],language=language)

            # Add successful result
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={
                    "organizations": entities[tak.ORGANIZATION.value],
                    "dateTime": entities[tak.DATETIME.value],
                    "IPAddress": entities[tak.IPADDRESS.value],
                    "persons": entities[tak.PERSON.value],
                    "personsType": entities[tak.PERSONTYPE.value],
                    "urls": entities[tak.URL.value],
                    "events": entities[tak.EVENT.value],
                    "emails": entities[tak.EMAIL.value],
                    "locations": entities[tak.LOCATION.value],
                    "phonesNumbers": entities[tak.PHONENUMBER.value],
                    "skills": entities[tak.SKILL.value],
                    "products": entities[tak.PRODUCT.value],
                    "quantities": entities[tak.QUANTITY.value],
                    "addresses": entities[tak.ADDRESS.value]
                },
                errors=None,
                warnings=None
            ))
            
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(ve)}",
                warnings=None
            ))
        except Exception as e:
            # Catch unexpected errors
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(e)}",
                warnings=None
            ))
    return  customskill_model.CustomSkillReturn(values=results).to_dict()  

async def image_embedding_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            url = record.data["url"]
            if not url:
                raise ValueError("Missing 'url' field in data")

            # Vactorize Image
            vector = imageanalytics_connector.image_embedding(img_url=url)

            # Add successful result
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={
                        csrk.IMG_VECTOR.value: vector["vector"]
                    },
                errors=None,
                warnings=None
            ))
            
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(ve)}",
                warnings=None
            ))
        except Exception as e:
            # Catch unexpected errors
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(e)}",
                warnings=None
            ))
    return customskill_model.CustomSkillReturn(values=results).to_dict() 

async def image_analysis_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            url = record.data["url"]
            if not url:
                raise ValueError("Missing 'url' field in data")

            # Analyze Image
            analyzed_image = imageanalytics_connector.analyze_image_from_url(img_url=url)

            # Add successful result
            img_read=""
            for line in analyzed_image["readResult"]["blocks"][0]["lines"]:
               img_read += f"{line['text']}\n" 
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={
                    csrk.IMG_CAPTION.value: analyzed_image["captionResult"]["text"],
                    csrk.IMG_DENSE_CAPTIONS.value:[captions["text"] for captions in analyzed_image["denseCaptionsResult"]["values"]],
                    csrk.IMG_TAGS.value: [tags["name"] for tags in analyzed_image["tagsResult"]["values"]],
                    csrk.IMG_READ.value: img_read
                    },
                errors=None,
                warnings=None
            ))
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(ve)}",
                warnings=None
            ))
        except Exception as e:
            # Catch unexpected errors
            results.append(customskill_model.SkillRecord(
                recordId=record_id,
                data={},
                errors=f"Unexpected error: {str(e)}",
                warnings=None
            ))
            
    return customskill_model.CustomSkillReturn(values=results).to_dict()
