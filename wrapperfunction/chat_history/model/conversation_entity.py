from datetime import datetime
from uuid import uuid4
from enum import Enum

class ConversationPropertyName(Enum):
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    USER_ID = "user_id"
    TIMESTAMP = "Timestamp"
    CONVERSATION_ID = "conversation_id"
    SENTIMENT = "sentiment"
    FEEDBACK = "feedback"
    BOT_NAME = "bot_name"

class ConversationEntity:
    def __init__(self, user_id: str, conversation_id: str, bot_name: str):
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.user_id = user_id
        self.timestamp = datetime.now().isoformat()
        self.conversation_id = conversation_id
        self.sentiment = ''
        self.feedback = ''
        self.bot_name = bot_name

    def to_dict(self):
        return {
            ConversationPropertyName.PARTITION_KEY.value: self.partition_key,
            ConversationPropertyName.ROW_KEY.value: self.row_key,
            ConversationPropertyName.USER_ID.value: self.user_id,
            ConversationPropertyName.TIMESTAMP.value: self.timestamp,
            ConversationPropertyName.CONVERSATION_ID.value: self.conversation_id,
            ConversationPropertyName.FEEDBACK.value: self.feedback,
            ConversationPropertyName.SENTIMENT.value: self.sentiment,
            ConversationPropertyName.BOT_NAME.value: self.bot_name
        }

