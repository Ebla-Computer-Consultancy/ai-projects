from datetime import datetime
from uuid import uuid4
class ConversationEntity:
    def __init__(self, user_id: str,conversation_id: str):
        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.user_id = user_id
        self.timestamp = datetime.now().isoformat()
        self.conversation_id = conversation_id
        self.sentiment = ''
        self.feedback = ''
    def to_dict(self):
        return {
            "PartitionKey": self.partition_key,
            "RowKey": self.row_key,
            "user_id": self.user_id,
            "Timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
            "feedback": self.feedback,
            "sentiment": self.sentiment
        }
    