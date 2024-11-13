from fastapi import HTTPException , File, Form
from fastapi.responses import JSONResponse

from wrapperfunction.admin.ctrl.admin_ctrl import resetIndexer, runIndexer
from wrapperfunction.admin.integration.crawl_integration import create_pdf_file, getAllNewsLinks, saveTopicsMedia
from wrapperfunction.admin.service import admin_service
from wrapperfunction.chatbot.integration.openai_connector import  chat_completion_mydata
from wrapperfunction.core.config import OPENAI_CHAT_MODEL, RERA_STORAGE_CONNECTION, SEARCH_KEY
from wrapperfunction.core.model.entity_setting import ChatbotSetting


async def media_search(search_text: str):
    try:
        user_message = f"write a long report in about 2 pages(reach the max)..about:{search_text}",
        
        system_message = "you are an assistant and expert in writing structured reports in a good way that write long reports from a given results"
        chat_history = [{"role": "system", "content": str(system_message)}]
        chat_history.append({"role": "user", "content": str(user_message)})

        chat_res = chat_completion_mydata(
            system_message=system_message,
            chatbot_setting=ChatbotSetting(index_name="rera-media", name=OPENAI_CHAT_MODEL),
            chat_history=chat_history
        )

        create_pdf_file(chat_res["message"]["content"],f"rera_reports/{search_text}.pdf")

        # Push the file to the Azure container
        push_To_Container(f"rera_reports", RERA_STORAGE_CONNECTION, "rera-media-reports")

        return JSONResponse(
            content={
                "report-text": chat_res["message"]["content"],
                "search_results": chat_res,
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def media_crawl(topics: list, urls: list):
    try:
        #1 get data
        links = getAllNewsLinks(urls=urls,media_config_path="wrapperfunction\core\settings\media.json")
        #2 save to blob storage
        saveTopicsMedia(
            news_links=links,
            config_file_path="wrapperfunction\core\settings\media.json", 
            topics=topics,container_name="rera-media",
            connection_string=RERA_STORAGE_CONNECTION
            )
        #3 reset indexer
        res = await admin_service.resetIndexer(name="rera-media-indexer")
        # # #4 run indexer
        res2 = await admin_service.runIndexer(name="rera-media-indexer")
        return JSONResponse(content={"message": "web crawl done succefuly"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


