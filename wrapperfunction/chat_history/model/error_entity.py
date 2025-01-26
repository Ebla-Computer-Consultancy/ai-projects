from datetime import datetime
from uuid import uuid4
from enum import Enum

class ErrorPropertyName(Enum):
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    TIMESTAMP = "timestamp"
    BOT_NAME= "bot_name"
    ERROR_MESSAGE= "error_message"
    STACK_TRACE= "stack_trace"
    CONVERSATION_ID= "conversation_id"
class ErrorEntity:
    def __init__(self,bot_name,error_message,stack_trace,conversation_id):
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.timestamp = datetime.now().isoformat()
        self.bot_name=bot_name
        self.error_message=error_message
        self.stack_trace=stack_trace
        self.conversation_id=conversation_id

    def to_dict(self):
        return {
            ErrorPropertyName.PARTITION_KEY.value: self.partition_key,
            ErrorPropertyName.ROW_KEY.value: self.row_key,
            ErrorPropertyName.TIMESTAMP.value: self.timestamp,
            ErrorPropertyName.BOT_NAME.value: self.bot_name,
            ErrorPropertyName.ERROR_MESSAGE.value: self.error_message,
            ErrorPropertyName.STACK_TRACE.value: self.stack_trace,
            ErrorPropertyName.CONVERSATION_ID.value: self.conversation_id
        }
