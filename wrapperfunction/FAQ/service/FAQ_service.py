
from typing import Optional
from wrapperfunction.FAQ.model.question_model import Question
from wrapperfunction.chat_history.service.chat_history_service import HTTPException, StatusCode
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn
import wrapperfunction.chat_history.integration.cosmos_db_connector as db_connector
from wrapperfunction.FAQ.model.question_entity import QuestionPropertyName, QuestionEntity

def get_question_data(RawKEY: str):
    try:
        filter = f"{QuestionPropertyName.ROW_KEY.value} eq '{RawKEY}'"
        return db_connector.get_entities(config.COSMOS_FAQ_TABLE, filter)[0]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retrieve questions: {str(e)}"
        )
async def add_questions(questions: list[Question]):
    try:
        print(questions)
        for question in questions:
            entity = QuestionEntity(question=question.Question, bot_name=question.BotName, total_count=question.TotalCount)
            await db_connector.add_entity(config.COSMOS_FAQ_TABLE, entity.to_dict())
        return ServiceReturn(
            status=StatusCode.SUCCESS,
            message="Questions added successfully."
        ).to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to add questions: {str(e)}"
        )

def delete_questions(RawKEY: str):
    try:
        question = get_question_data(RawKEY)
        if question:
            db_connector.delete_entity(config.COSMOS_FAQ_TABLE, question)
            return ServiceReturn(
                status=StatusCode.SUCCESS,
                message="Question deleted successfully."
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_question(RawKEY: str, updated_data: Question):
    try:
        question = get_question_data(RawKEY)
        if question:
            question.update(updated_data)
            db_connector.update_entity(config.COSMOS_FAQ_TABLE, question)
            return ServiceReturn(
            status=StatusCode.SUCCESS,
            message="Question updated successfully.").to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
def get_questions(bot_name: Optional[str] = None,n= None):
    try:
        filter_condition = f"{QuestionPropertyName.BOT_NAME.value} eq '{bot_name}'" if bot_name else None
        res=db_connector.get_entities(config.COSMOS_FAQ_TABLE, filter_condition)
        filtered_res = sorted(({QuestionPropertyName.ROW_KEY.value: item[QuestionPropertyName.ROW_KEY.value],QuestionPropertyName.ACTUAL_QUESTION.value: item[QuestionPropertyName.ACTUAL_QUESTION.value],QuestionPropertyName.TOTAL_COUNT.value: item[QuestionPropertyName.TOTAL_COUNT.value],}for item in res),key=lambda x: x[QuestionPropertyName.TOTAL_COUNT.value],reverse=True)
        if n != None:
            return filtered_res[:n]
        return filtered_res
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retrieve questions: {str(e)}")  