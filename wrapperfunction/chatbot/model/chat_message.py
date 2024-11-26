from pydantic import BaseModel
from enum import Enum

Roles = Enum(
    "Roles",
    {
        "User": "user",
        "Assistant": "assistant",
        "Error": "error",
        "Tool": "tool",
        "Function": "function",
        "System": "system",
    },
)
Message_Type=Enum(
    "Message_Type",
    {
        "Message": "message",
        "Document": "document",
    },
)



class ChatMessage(BaseModel):
    content: str
    role: Roles

    class Config:
        use_enum_values = True