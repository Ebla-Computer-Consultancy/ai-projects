from pydantic import BaseModel
from typing import List

class Map(BaseModel):
    name: str
    source: str
    inputs: list

class Output(BaseModel):
    name: str
    targetName: str    
    
class Selector(BaseModel):
    targetIndexName: str
    parentKeyFieldName: str
    sourceContext: str
    mappings: List[Map]

class indexProjections(BaseModel):
    selectors: List[Selector]
    parameters : dict = {"projectionMode": "skipIndexingParentDocuments"}
      
class SkillSet:
    def __init__(self,name: str, description: str | None ,skills: List[dict], indexProjections: indexProjections):
        self.name = name
        self.description = description
        self.skills = skills
        self.indexProjections = indexProjections
        
    def to_dict(self):
        return{
           "name": self.name,
           "description": self.description,
           "skills": self.skills,
           "indexProjections": self.indexProjections
        }

