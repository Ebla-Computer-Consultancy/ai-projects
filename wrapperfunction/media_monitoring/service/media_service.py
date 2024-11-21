from fastapi import HTTPException
from fastapi.responses import JSONResponse
from wrapperfunction.admin.integration.crawl_integration import create_pdf_file, getAllNewsLinks, saveTopicsMedia
from wrapperfunction.admin.integration import storage_connector
from wrapperfunction.admin.integration.textanalytics_connector import analyze_sentiment, detect_language, entity_recognition, extract_key_phrases
from wrapperfunction.admin.service import admin_service
from wrapperfunction.chatbot.integration.openai_connector import  chat_completion
from wrapperfunction.core import config
from wrapperfunction.core.model.entity_setting import ChatbotSetting, CustomSettings
from wrapperfunction.core.model.service_return import ServiceReturn, StatusCode
from wrapperfunction.chatbot.service import chatbot_service
from fastapi.responses import FileResponse

async def media_search(search_text: str):
    try:
        user_message = f"write a long report in about 2 pages(reach the max)..about:{search_text}",
        
        chat_settings = config.load_chatbot_settings(bot_name="media")
        print(chat_settings.index_name)
        chat_history = [{"role": "system", "content": chat_settings.system_message}]
        chat_history.append({"role": "user", "content": str(user_message)})

        chat_res = chat_completion(
            chatbot_setting=chat_settings,
            chat_history=chat_history
        )
        report_file_name = search_text.replace(" ","_")
        # create_pdf_file(chat_res["message"]["content"],f"{report_file_name}.pdf")
        storage_connector.upload_json_to_azure(content=chat_res["message"]["content"],
                                              connection_string= config.RERA_STORAGE_CONNECTION,
                                              container_name= "rera-media-reports",
                                              blob_name=f"{report_file_name}.txt")
        
        sas_url = storage_connector.generate_blob_sas_url(connection_string= config.RERA_STORAGE_CONNECTION,
                                              container_name= "rera-media-reports",
                                              blob_name=f"{report_file_name}.txt")
        # Push the file to the Azure container
        return ServiceReturn(
            status=StatusCode.CREATED,
            message=f"{search_text} Report Generated Successfuly",
            data={
                "report_url": sas_url,
            }
        ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def media_crawl(topics: list, urls: list):
    try:
        #1 get data
        links = getAllNewsLinks(urls=urls)
        #2 save to blob storage
        saveTopicsMedia(
            news_links=links,
            topics=topics,
            container_name="rera-media",
            connection_string=config.RERA_STORAGE_CONNECTION
            )
        #3 reset indexer
        res = await admin_service.resetIndexer(name="rera-media-test-indexer")
        # # #4 run indexer
        res2 = await admin_service.runIndexer(name="rera-media-test-indexer")
        return ServiceReturn(
                            status=StatusCode.SUCCESS,
                            message=f"URL's:{urls} | Topics:{topics} crawled succefuly", 
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
            sentiment = analyze_sentiment([text])

            # Add successful result
            results.append({
                "recordId": record_id,
                "data": {
                    "sentimentLabel": sentiment
                },
                "errors": None,
                "warnings": None
            })
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": str(ve),
                "warnings": None
            })
        except Exception as e:
            # Catch unexpected errors
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": f"Unexpected error: {str(e)}",
                "warnings": None
            })

    return {"values": results}

async def detect_language_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            text = record.data["text"]
            if not text:
                raise ValueError("Missing 'text' field in data")

            # Analyze sentiment
            detected_language = detect_language(messages=[text])

            # Add successful result
            results.append({
                "recordId": record_id,
                "data": {
                    "language_name": detected_language["name"],
                    "language_iso6391_name": detected_language["iso6391_name"] 
                },
                "errors": None,
                "warnings": None
            })
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": str(ve),
                "warnings": None
            })
        except Exception as e:
            # Catch unexpected errors
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": f"Unexpected error: {str(e)}",
                "warnings": None
            })
    return {"values":results}
    
async def extract_key_phrases_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            text = record.data["text"]
            language = record.data["language"]
            if not text:
                raise ValueError("Missing 'text' field in data")

            # Analyze sentiment
            key_phrases = extract_key_phrases(messages=[text],language=language)

            # Add successful result
            results.append({
                "recordId": record_id,
                "data": {
                    "keyphrases": key_phrases
                },
                "errors": None,
                "warnings": None
            })
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": str(ve),
                "warnings": None
            })
        except Exception as e:
            # Catch unexpected errors
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": f"Unexpected error: {str(e)}",
                "warnings": None
            })
    return  {"values": results}

async def entity_recognition_skill(values: list):
    results = []
    for record in values:
        record_id = record.recordId  
        try:
            
            text = record.data["text"]
            language = record.data["language"]
            if not text:
                raise ValueError("Missing 'text' field in data")

            # Analyze sentiment
            entities = entity_recognition(messages=[text],language=language)

            # Add successful result
            results.append({
                "recordId": record_id,
                "data": {
                    "organizations": entities["Organization"],
                    "dateTime": entities["DateTime"],
                    "IPAddress": entities["IPAddress"],
                    "persons": entities["Person"],
                    "personsType": entities["PersonType"],
                    "urls": entities["URL"],
                    "events": entities["Event"],
                    "emails": entities["Email"],
                    "locations": entities["Location"],
                    "phonesNumbers": entities["PhoneNumber"],
                    "skills": entities["Skill"],
                    "products": entities["Product"],
                    "quantities": entities["Quantity"],
                    "addresses": entities["Address"],
                    "entities": entities["entities"],
                },
                "errors": None,
                "warnings": None
            })
        except ValueError as ve:
            # Handle missing or invalid fields
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": str(ve),
                "warnings": None
            })
        except Exception as e:
            # Catch unexpected errors
            results.append({
                "recordId": record_id,
                "data": {},
                "errors": f"Unexpected error: {str(e)}",
                "warnings": None
            })
    return {"values": results}   