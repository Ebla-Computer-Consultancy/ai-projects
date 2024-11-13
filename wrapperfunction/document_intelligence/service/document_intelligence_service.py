import json
from fastapi import File, HTTPException, UploadFile
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.core import config
import wrapperfunction.document_intelligence.integration.document_intelligence_connector as documentintelligenceconnector
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice


def analyze_file(model_id: str, bot_name: str, file: UploadFile = File()):
    try:
        poller_result = documentintelligenceconnector.analyze_file(file, model_id)
        file_result = {"content": poller_result.content, "tables": []}
        for index, table in enumerate(poller_result.tables):
            file_result["tables"].append({"cells": []})
            for cell in table["cells"]:
                file_result["tables"][index]["cells"].append(
                    {"content": cell["content"], "kind": cell.kind}
                )
        chatbot_settings = config.load_chatbot_settings(bot_name)
        chatbot_settings.examples.append(
            {"role": "user", "content": json.dumps(file_result)}
        )

        return chatbotservice.ask_open_ai_chatbot(
            bot_name=bot_name,
            chat_payload=ChatPayload(messages=chatbot_settings.examples),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
