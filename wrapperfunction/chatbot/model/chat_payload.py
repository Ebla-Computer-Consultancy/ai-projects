from pydantic import BaseModel
from typing import List, Optional
from wrapperfunction.chatbot.model.chat_message import ChatMessage


class ChatPayload(BaseModel):
    messages: List[ChatMessage]  # A list of ChatMessage objects
    stream_id: Optional[str] = None  # Nullable stream_id string with default None
