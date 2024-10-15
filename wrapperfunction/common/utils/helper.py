from datetime import datetime
from uuid import uuid4
from enum import Enum

class Role(Enum):
    User = "user"
    Assistant = "assistant"


class ChatEntity:
    def __init__(self, user_id: str, content: str = 'User Starts New Chat', role: str = Role.User.value):
        self.partition_key = user_id
        self.row_key = str(uuid4())
        self.content = content
        self.role = role
        self.timestamp = datetime.now().isoformat()
        self.conversation_id = str(uuid4())

    def to_dict(self):
        return {
            "PartitionKey": self.partition_key,
            "RowKey": self.row_key,
            "content": self.content,
            "Role": self.role,
            "Timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
        }