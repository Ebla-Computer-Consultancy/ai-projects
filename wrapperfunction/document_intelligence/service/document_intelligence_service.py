import json
from fastapi import File, HTTPException, UploadFile
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
import wrapperfunction.document_intelligence.integration.document_intelligence_connector as documentintelligenceconnector
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice

def inline_read_scanned_pdf(file: UploadFile | None, file_bytes: bytes = None):
    if file or file_bytes:
        result = documentintelligenceconnector.analyze_file(file, "prebuilt-read", file_bytes)

        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
        return extracted_text

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
        for i in range(3):
            
            res = chatbotservice.ask_open_ai_chatbot(
                bot_name=bot_name,
                chat_payload=ChatPayload(
                    messages=[
                        {
                            "role": "user",
                            "content": json.dumps(
                                file_result,
                                ensure_ascii=False,
                            ),
                        }
                    ]
                ),
            )
        
            data = validate_json(res[0])
            if data != "False":
                return data
        raise HTTPException(status_code=500, detail="Can not Analyze this document")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def validate_json(data: str):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return "False"