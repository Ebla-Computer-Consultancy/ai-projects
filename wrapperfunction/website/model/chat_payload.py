from pydantic import BaseModel
from typing import List, Optional
from wrapperfunction.website.model.chat_message import ChatMessage


class ChatPayload(BaseModel):
    messages: List[ChatMessage]  # A list of ChatMessage objects
    stream_id: Optional[str] = None  # Nullable stream_id string with default None
    conversation_id: Optional[str] = None
    user_id: Optional[str]
