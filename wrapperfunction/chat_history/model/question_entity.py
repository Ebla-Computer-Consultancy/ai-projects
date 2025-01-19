from uuid import uuid4
from enum import Enum

class QuestionPropertyName(Enum):
    ID = "QuestionId"
    ACTUAL_QUESTION = "ActualQuestion"
    BOT_NAME = "botname"
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    TOTAL_COUNT = "TotalCount"

class QuestionEntity:
    def __init__(self, question: str, bot_name: str, total_count: int ):
        self.id = str(uuid4())
        self.question = question
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.bot_name = bot_name
        self.total_count = total_count  



    def to_dict(self):
        return {
            QuestionPropertyName.PARTITION_KEY.value: self.partition_key,
            QuestionPropertyName.ROW_KEY.value: self.row_key,
            QuestionPropertyName.ID.value: self.id,
            QuestionPropertyName.QUESTION.value: self.question,
            QuestionPropertyName.BOT_NAME.value: self.bot_name,
            QuestionPropertyName.TOTALCOUNT.value: self.total_count,
        }
