from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from bson import ObjectId
from pydantic_core import core_schema
from schemas.pyobjectid_schemas import PyObjectId

class GroupResponse(BaseModel):
    id: str
    name: str

class StudentResponse(BaseModel):
    id: str
    ho_ten: str

class ProjectResponse(BaseModel):
    id: str
    title: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    group_id: PyObjectId
    assigned_student_ids: List[str]
    status: Optional[str] = "pending"
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: PyObjectId
    title: str
    description: Optional[str]
    group: Optional[GroupResponse]
    assigned_students: Optional[List[StudentResponse]]
    status: Optional[str]
    deadline: Optional[datetime]
    related_to_project: Optional[ProjectResponse]

    class Config:
        from_attributes = True