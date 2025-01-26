import datetime
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4
from pydantic import BaseModel
class Prompt(BaseModel):
    prompt: str

class SubmitForm(BaseModel):
    form:dict

class FormStatus(Enum):
    APPROVED = 0
    REJECTED = 1
    PENDING = 2
    
class VacationTypes(Enum):
    SickLeave="Sick Leave"
    PersonalLeave="Personal Leave"
    PublicHolidays="Public Holidays"
    UnpaidLeave= "Unpaid Leave"
    YearVacation="Year Vacation"
    
    def to_list():
        return[
            VacationTypes.SickLeave.value,
            VacationTypes.PersonalLeave.value,
            VacationTypes.PublicHolidays.value,
            VacationTypes.UnpaidLeave.value,
            VacationTypes.YearVacation
        ]

class DepartmentTypes(Enum):
    AI = "AI"
    PM = "PM"
    HR = "HR"
    SE = "SE"
    IT = "IT"
    def to_list():
        return[
           DepartmentTypes.AI.value,
           DepartmentTypes.PM.value,
           DepartmentTypes.HR.value,
           DepartmentTypes.SE.value,
           DepartmentTypes.IT.value 
        ]
class VacationForm(BaseModel):
    vacation_type: str
    employee_name: str
    employee_ID: int
    manager_name: str
    employee_department: str
    start_date: str
    end_date: str
    comments: str

class VacationFormEntity:
    def __init__(self,vacation_type: str,
    employee_name: str,
    employee_ID: int,
    manager_name: str,
    employee_department: str,
    start_date: str,
    end_date: str,
    comments: str):
        self.vacation_type = vacation_type
        self.employee_name = employee_name
        self.employee_ID = employee_ID
        self.manager_name = manager_name
        self.employee_department = employee_department
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.total_days = (datetime.strptime(end_date, '%Y-%m-%d') - 
                        datetime.strptime(start_date, '%Y-%m-%d')).days
        self.comments = comments
    
    def to_dict(self):
        return {
            "PartitionKey":str(uuid4()),
            "RowKey":str(uuid4()),
            "Vacation_Type":self.vacation_type,
            "Employee_ID":self.employee_ID,
            "Employee_Name":self.employee_name,
            "Manager_Name":self.manager_name,
            "Department":self.employee_department,
            "Start_Date":self.start_date,
            "End_Date":self.end_date,
            "Total_Days":self.total_days,
            "Status":FormStatus.PENDING.value,
            "Comments":self.comments
        }
class Status(BaseModel):
    employee_ID:int
    
class GetForm(BaseModel):
    column_name:str
    value:str

class ToolCall(BaseModel):
    function_name: str
    function_args: dict
    
class ActionResponse(BaseModel):
    actions: Optional[List[ToolCall]] = None
    message: Optional[str] = None