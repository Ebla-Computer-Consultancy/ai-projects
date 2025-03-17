from typing import List, Optional
from wrapperfunction.FAQ.model.question_model import Question
from wrapperfunction.chat_history.service.chat_history_service import HTTPException, StatusCode
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.FAQ.model.question_entity import QuestionPropertyName

def get_max_order_index(bot_name: str) -> int:
    try:
        filter_condition = f"{QuestionPropertyName.BOT_NAME.value} eq '{bot_name}'"
        results = db_connector.get_entities(config.COSMOS_ARCHIVED_FAQ_TABLE, filter_condition)
        if not results:
            return 0
        return max(item.get("OrderIndex", 0) for item in results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve max order index for bot '{bot_name}': {str(e)}")


def get_all_faqs(bot_name: str) -> List[dict]:
    try:
        filter_condition = f"{QuestionPropertyName.BOT_NAME.value} eq '{bot_name}'" 
        return db_connector.get_entities(config.COSMOS_FAQ_TABLE, filter_condition)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve all FAQs: {str(e)}")
    
def get_archived_faqs(bot_name: str, limit: Optional[int] = None) -> List[Question]:
    try:
        filter_condition = f"{QuestionPropertyName.BOT_NAME.value} eq '{bot_name}'"
        results = db_connector.get_entities(config.COSMOS_ARCHIVED_FAQ_TABLE, filter_condition)
        sorted_results = sorted(
            (
                {
                    QuestionPropertyName.PARTITION_KEY.value: item[QuestionPropertyName.PARTITION_KEY.value],
                    QuestionPropertyName.ROW_KEY.value: item[QuestionPropertyName.ROW_KEY.value],
                    QuestionPropertyName.ACTUAL_QUESTION.value: item[QuestionPropertyName.ACTUAL_QUESTION.value],
                    QuestionPropertyName.TOTAL_COUNT.value: item[QuestionPropertyName.TOTAL_COUNT.value],
                    QuestionPropertyName.ORDER_INDEX.value: item[QuestionPropertyName.ORDER_INDEX.value],
                    QuestionPropertyName.BOT_NAME.value: item[QuestionPropertyName.BOT_NAME.value],
                }
                for item in results
            ),
            key=lambda x: x[QuestionPropertyName.ORDER_INDEX.value],
            reverse=False,
        )
        return sorted_results[:limit] if limit is not None else sorted_results
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve archived FAQs: {str(e)}")  

async def add_faqs_to_archive(faqs_data: list, bot_name: str) -> dict:
    try:
        existing_faqs = {faq[QuestionPropertyName.ACTUAL_QUESTION.value] for faq in get_archived_faqs(bot_name)}
        max_order = get_max_order_index(bot_name)

        for faq_data in faqs_data:
            if faq_data["ActualQuestion"] in existing_faqs:
                continue
            max_order += 1
            faq_data["OrderIndex"] = max_order
            await db_connector.add_entity(config.COSMOS_ARCHIVED_FAQ_TABLE, faq_data)

        return ServiceReturn(status=StatusCode.SUCCESS, message="FAQs added to archive.").to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive FAQs: {str(e)}")

def get_archived_faq(row_key: str) -> dict:
    try:
        filter_condition = f"{QuestionPropertyName.ROW_KEY.value} eq '{row_key}'"
        results = db_connector.get_entities(config.COSMOS_ARCHIVED_FAQ_TABLE, filter_condition)
        if results:
            return results[0]
        raise HTTPException(status_code=404, detail="FAQ not found in archive.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve archived FAQ: {str(e)}")

def update_archived_faq(row_key: str, updated_data: Question) -> dict:
    try:
        faq = get_archived_faq(row_key)
        if faq:
            db_connector.update_entity(config.COSMOS_ARCHIVED_FAQ_TABLE, {**faq, **updated_data.model_dump()})
            return ServiceReturn(status=StatusCode.SUCCESS, message="FAQ updated in archive.").to_dict()
        raise HTTPException(status_code=404, detail="FAQ not found in archive.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update archived FAQ: {str(e)}")

def delete_archived_faqs(faqs_data: list) -> dict:
    try:
        for faq in faqs_data:
            db_connector.delete_entity(config.COSMOS_ARCHIVED_FAQ_TABLE, faq)
        
        return ServiceReturn(status=StatusCode.SUCCESS, message="FAQs deleted from archive.").to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete archived FAQs: {str(e)}")
