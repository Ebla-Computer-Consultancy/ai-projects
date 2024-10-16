from datetime import datetime
from uuid import uuid4
from enum import Enum

class Role(Enum):
    User = "user"
    Assistant = "assistant"


class ConversationEntity:
    def __init__(self, user_id: str):
        self.partition_key = user_id
        self.row_key = str(uuid4())
        self.timestamp = datetime.now().isoformat()
        self.conversation_id = str(uuid4())
        self.sentiment = ''
        self.feedback = ''
    def to_dict(self):
        return {
            "PartitionKey": self.partition_key,
            "RowKey": self.row_key,
            "Timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
            "feedback": self.feedback,
            "sentiment": self.sentiment
        }
    
class UserEntity:
    def __init__(self, user_id: str, email: str, password: str):
        self.partition_key = user_id
        self.row_key = email
        self.password = password
    def to_dict(self):
        return {
            "PartitionKey": self.partition_key,
            "RowKey": self.row_key,
            "password": self.password
    }    

class MessageEntity:
    def __init__(self, user_id: str, content: str, conversation_id: str, role: Role):
        self.partition_key = user_id
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