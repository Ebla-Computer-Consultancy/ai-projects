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




class ChatMessage(BaseModel):
    content: str
    role: Roles

    class Config:
        use_enum_values = True