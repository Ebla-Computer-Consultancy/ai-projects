import azure.functions as func
from wrapperfunction.chat_history.model.message_entity import MessagePropertyName
from wrapperfunction.chat_history.service.chat_history_service import CheckQuestionAnswered, StatusCode, get_question_answer_pairs, update_message
from wrapperfunction.core.model.service_return import ServiceReturn

chat_history_bp= func.Blueprint()

chat_history_bp.function_name("chat_history_bp")



@chat_history_bp.schedule(arg_name="CheckAnsweredTimer", schedule="0 0 * * *")
def daily_schedule_Update_Answer_Entities(CheckAnsweredTimer: func.TimerRequest):

    try:
        all_qna_pairs = get_question_answer_pairs()
        
        for pair in all_qna_pairs:
            question = pair.get("question", {})
            answer = pair.get("answer", {})
            answer_message_id = answer.get("message_id")
            question_message_id = question.get("message_id")

            if answer_message_id:
                is_answer = CheckQuestionAnswered(
                    question.get("content"), 
                    answer.get("content"), 
                )
                updated_data = {MessagePropertyName.IS_ANSWERED.value: is_answer}
                update_message(updated_data, message_ids=[answer_message_id, question_message_id])

        return ServiceReturn(status=StatusCode.SUCCESS, message="Answer entities updated successfully").to_dict()
    except Exception as e:
        return ServiceReturn(status=StatusCode.INTERNAL_SERVER_ERROR, message=f"Error occurred: {str(e)}").to_dict()
    
