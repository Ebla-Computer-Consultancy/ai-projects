from datetime import datetime
from uuid import uuid4
from enum import Enum
from wrapperfunction.chatbot.model.chat_message import Roles

class MessagePropertyName(Enum):
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    TIMESTAMP = "Timestamp"
    CONTENT = "content"
    CONVERSATION_ID = "conversation_id"
    ROLE = "role"

class MessageEntity:
    def __init__(self, content: str, conversation_id: str, role: Roles):
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.timestamp = datetime.now().isoformat()
        self.content = content
        self.conversation_id = conversation_id
        self.role = role

    def to_dict(self):
        return {
            MessagePropertyName.PARTITION_KEY.value: self.partition_key,
            MessagePropertyName.ROW_KEY.value: self.row_key,
            MessagePropertyName.TIMESTAMP.value: self.timestamp,
            MessagePropertyName.CONTENT.value: self.content,
            MessagePropertyName.CONVERSATION_ID.value: self.conversation_id,
            MessagePropertyName.ROLE.value: self.role
        }


