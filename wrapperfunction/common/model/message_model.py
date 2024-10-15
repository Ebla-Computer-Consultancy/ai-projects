from pydantic import BaseModel
from wrapperfunction.common.utils.helper import Role
class message(BaseModel):
    user_id: str
    content: str
    conversation_id: str
    Role:Role