from typing import Optional, List
from pydantic import BaseModel

class Prompt(BaseModel):
    prompt: str

class SubmitForm(BaseModel):
    form:dict

class VacationForm(BaseModel):
    type: str
    employee_name: str
    employee_ID: int
    manager_name: str
    employee_department: str
    start_date: str
    end_date: str
    total_days: int
    status: str
    comments: str
        
class Status(BaseModel):
    employee_ID:int
    
class GetForm(BaseModel):
    coulomn_name:str
    value:str

class ToolCall(BaseModel):
    function_name: str
    function_args: dict
    
class ActionResponse(BaseModel):
    actions: Optional[List[ToolCall]] = None
    message: Optional[str] = None