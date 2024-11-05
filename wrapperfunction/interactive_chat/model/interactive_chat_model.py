from typing import Optional, List
from pydantic import BaseModel

class Prompt(BaseModel):
    prompt: str

class SubmitForm(BaseModel):
    form:dict
    
class Status(BaseModel):
    employee_name:str
    employee_department:str
    
class GetForm(BaseModel):
    coulomn_name:str
    value:str

class ToolCall(BaseModel):
    function_name: str
    function_args: dict
    
class ActionResponse(BaseModel):
    actions: Optional[List[ToolCall]] = None
    message: Optional[str] = None