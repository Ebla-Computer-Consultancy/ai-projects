
from wrapperfunction.chat_history.service import chat_history_service
from fastapi import HTTPException
import wrapperfunction.text_analysis.integration.textanalytics_connector as text_connector

def perform_semantic_analysis():
    try:
        conversations=chat_history_service.get_all_conversations()
        for conversation in conversations:
            if conversation["sentiment"] is "":
                conversation_id = conversation["conversation_id"]
                messages = chat_history_service.get_chat_history(conversation_id)
                message_texts = [msg["content"] for msg in messages if "content" in msg]
                if not message_texts:
                    raise HTTPException(status_code=400, detail="No valid messages found for semantic analysis.")
                semantic_data = text_connector.analyze_sentiment(message_texts)
                chat_history_service.update_conversation(conversation_id, {"sentiment": semantic_data}) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def perform_feedback_update(conversation_id: str, feedback: int):
    try:

        chat_history_service.update_conversation(conversation_id, {"feedback": feedback})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))