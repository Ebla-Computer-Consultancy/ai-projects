from pydantic import BaseModel
from wrapperfunction.common.model.role import Role
class message(BaseModel):
    user_id: str
    content: str
    conversation_id: str
    Role:Role

class user(BaseModel):
    email: str
    password: str    