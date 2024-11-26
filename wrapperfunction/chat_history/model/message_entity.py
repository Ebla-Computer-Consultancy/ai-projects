from datetime import datetime
import json
from uuid import uuid4
from enum import Enum
from wrapperfunction.chatbot.model.chat_message import Roles,MessageType

class MessagePropertyName(Enum):
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    TIMESTAMP = "timestamp"
    CONTENT = "content"
    CONVERSATION_ID = "conversation_id"
    ROLE = "role"
    CONTEXT = "context"
    MessageType = "MessageType"

class MessageEntity:
    def __init__(self, content: str, conversation_id: str, role: Roles, context: str, type:MessageType=MessageType.Message.value):
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.timestamp = datetime.now().isoformat()  
        self.content = content
        self.conversation_id = conversation_id
        self.role = role
        self.context = context
        self.type = type

    def to_dict(self):
        return {
            MessagePropertyName.PARTITION_KEY.value: self.partition_key,
            MessagePropertyName.ROW_KEY.value: self.row_key,
            MessagePropertyName.TIMESTAMP.value: self.timestamp,
            MessagePropertyName.CONTENT.value: self.content,
            MessagePropertyName.CONVERSATION_ID.value: self.conversation_id,
            MessagePropertyName.ROLE.value: self.role,
            MessagePropertyName.CONTEXT.value: self.context,
            MessagePropertyName.MessageType.value: self.type            
        }

