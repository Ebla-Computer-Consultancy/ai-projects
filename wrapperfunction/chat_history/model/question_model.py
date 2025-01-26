from pydantic import BaseModel


class Question(BaseModel):
    Question: str
    BotName: str
    TotalCount: int