from pydantic import BaseModel


class TextRenderingPayload(BaseModel):
    text: str
    is_ar: bool = True