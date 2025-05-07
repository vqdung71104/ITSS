from typing import Optional, List, Any
from pydantic import BaseModel
from bson import ObjectId
from bson import Regex
from pydantic_core import core_schema



class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    mentor_id: Optional[str]
    group_ids: Optional[List[str]]
    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    mentor_id: Optional[str]
    group_ids: Optional[List[str]]
    class Config:
        from_attributes = True