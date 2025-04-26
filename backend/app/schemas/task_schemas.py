from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    group_id: str
    assigned_student_ids: List[str]
    status: Optional[str] = "pending"
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    group: Optional[dict]
    assigned_students: Optional[List[dict]]
    status: Optional[str]
    deadline: Optional[datetime]
    related_to_project: Optional[dict]

    class Config:
        from_attributes = True