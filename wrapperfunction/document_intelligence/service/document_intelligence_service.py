import json
from fastapi import File, HTTPException, UploadFile
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.core import config
import wrapperfunction.document_intelligence.integration.document_intelligence_connector as documentintelligenceconnector
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice


def analyze_file(model_id: str, file: UploadFile = File()):
    try:
        poller_result = documentintelligenceconnector.analyze_file(file, model_id)
        file_result = {"content": poller_result.content, "tables": []}
        for index, table in enumerate(poller_result.tables):
            file_result["tables"].append({"cells": []})
            for cell in table["cells"]:
                file_result["tables"][index]["cells"].append(
                    {"content": cell["content"], "kind": cell.kind}
                )
        entity_settings = config.load_entity_settings()
        entity_settings["examples"].append(
            {"role": "user", "content": json.dumps(file_result)}
        )

        return chatbotservice.ask_open_ai_chatbot(
            bot_name="document_intelligence_chatbot",
            chat_payload=ChatPayload(messages=entity_settings["examples"]),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
