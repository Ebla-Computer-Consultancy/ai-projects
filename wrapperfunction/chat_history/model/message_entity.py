from datetime import datetime
from uuid import uuid4
from enum import Enum

from wrapperfunction.chatbot.model.chat_message import Roles,MessageType

class MessagePropertyName(Enum):
    PARTITION_KEY = "PartitionKey"
    ROW_KEY = "RowKey"
    MESSAGE_ID = "message_id"
    TIMESTAMP = "timestamp"
    CONTENT = "content"
    CONVERSATION_ID = "conversation_id"
    ROLE = "role"
    CONTEXT = "context"
    COMPLETIONTOKENS="completion_tokens"
    PROMPTTOKENS="prompt_tokens"
    TOTALTOKENS="total_tokens"
    MessageType = "MessageType"
    FEEDBACK = "feedback"
    IS_ANSWERED = "is_answered"



class MessageEntity:
    def __init__(self, content: str, conversation_id: str, role: Roles, context: str,type:MessageType=MessageType.Message.value,completion_tokens=None,prompt_tokens=None,total_tokens=None):

        self.partition_key = str(uuid4())
        self.row_key = str(uuid4())
        self.message_id = str(uuid4())
        self.timestamp = datetime.now().isoformat()  
        self.content = content
        self.conversation_id = conversation_id
        self.role = role
        self.context = context
        self.type = type
        self.completion_tokens=completion_tokens
        self.prompt_tokens=prompt_tokens
        self.total_tokens=total_tokens
        self.feedback="undefined"
        self.is_answered="undefined"




    def to_dict(self):
        return {
            MessagePropertyName.PARTITION_KEY.value: self.partition_key,
            MessagePropertyName.ROW_KEY.value: self.row_key,
            MessagePropertyName.MESSAGE_ID.value: self.message_id,
            MessagePropertyName.TIMESTAMP.value: self.timestamp,
            MessagePropertyName.CONTENT.value: self.content,
            MessagePropertyName.CONVERSATION_ID.value: self.conversation_id,
            MessagePropertyName.ROLE.value: self.role,
            MessagePropertyName.CONTEXT.value: self.context,
            MessagePropertyName.MessageType.value: self.type,
            MessagePropertyName.COMPLETIONTOKENS.value: self.completion_tokens,
            MessagePropertyName.PROMPTTOKENS.value: self.prompt_tokens,
            MessagePropertyName.TOTALTOKENS.value: self.total_tokens,
            MessagePropertyName.FEEDBACK.value: self.feedback,
            MessagePropertyName.IS_ANSWERED.value: self.is_answered

                



        }
