from enum import Enum
from pydantic import BaseModel
from typing import List

class CustomSkillReturnKeys(Enum):
    VALUES = "values"
    KEYPHRASES = "keyphrases"
    SENTIMENT = "sentimentLabel"
    IMG_VECTOR = "image_vector"
    IMG_CAPTION = "image_caption"
    IMG_DENSE_CAPTIONS= "image_denseCaptions"
    IMG_TAGS = "image_tags"
    IMG_READ = "image_read"

class SkillRecord(BaseModel):
    recordId: str
    data: dict
    errors: str | None = None,
    warnings: str | None = None
    
class CustomSkillRequest(BaseModel):
    values: List[SkillRecord]

class CustomSkillReturn:
    def  __init__(self,values: List[SkillRecord]):
        self.values = values
    
    def to_dict(self):
        return{
            CustomSkillReturnKeys.VALUES.value: self.values
        } 