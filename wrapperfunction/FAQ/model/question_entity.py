from uuid import uuid4
from enum import Enum

class QuestionPropertyName(Enum):
    ACTUAL_QUESTION = "ActualQuestion"
    BOT_NAME = "botname"
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    TOTAL_COUNT = "TotalCount"
    ORDER_INDEX = "OrderIndex"

class QuestionEntity:
    def __init__(self, question: str, bot_name: str, total_count: int, order_index: int):
        self.question = question
        self.partition_key = "FAQCluster"
        self.row_key = str(uuid4())
        self.bot_name = bot_name
        self.total_count = total_count  
        self.order_index = order_index



    def to_dict(self):
        return {
            QuestionPropertyName.PARTITION_KEY.value: self.partition_key,
            QuestionPropertyName.ROW_KEY.value: self.row_key,
            QuestionPropertyName.ACTUAL_QUESTION.value: self.question,
            QuestionPropertyName.BOT_NAME.value: self.bot_name,
            QuestionPropertyName.TOTAL_COUNT.value: self.total_count,
            QuestionPropertyName.ORDER_INDEX.value: self.order_index
        }
