from uuid import uuid4
from enum import Enum

class QuestionPropertyName(Enum):
    ID = "QuestionId"
    QUESTION = "Question"
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"

class QuestionEntity:
    def __init__(self, question: str):
        self.id = str(uuid4())
        self.question = question
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())  

    def to_dict(self):
        return {
            QuestionPropertyName.PARTITION_KEY.value: self.partition_key,
            QuestionPropertyName.ROW_KEY.value: self.row_key,
            QuestionPropertyName.ID.value: self.id,
            QuestionPropertyName.QUESTION.value: self.question,
        }
