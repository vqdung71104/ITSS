from pydantic import BaseModel
from typing import Optional, List

class GroupCreate(BaseModel):
    name: str
    project_id: str

class GroupResponse(BaseModel):
    id: str
    name: str
    project: Optional[dict]
    leaders: Optional[dict]
    members: Optional[List[dict]]
    allTasks: Optional[List[dict]]

    class Config:
        from_attributes = True