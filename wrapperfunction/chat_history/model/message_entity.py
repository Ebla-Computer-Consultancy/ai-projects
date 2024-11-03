from datetime import datetime
from uuid import uuid4
from wrapperfunction.chatbot.model.chat_message import Roles

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
            "PartitionKey": self.partition_key,
            "RowKey": self.row_key,
            "Timestamp": self.timestamp,
            "content": self.content,
            "conversation_id": self.conversation_id,
            "role": self.role
        }