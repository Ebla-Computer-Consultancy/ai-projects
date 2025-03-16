from pydantic import BaseModel


class Question(BaseModel):
    ActualQuestion: str
    botname: str
    TotalCount: int
    OrderIndex: int