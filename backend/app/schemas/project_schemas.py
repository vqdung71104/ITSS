from typing import Optional, List, Any
from pydantic import BaseModel
from schemas.pyobjectid_schemas import PyObjectId
from bson import ObjectId
from schemas.user_schemas import UserResponse
from schemas.group_schemas import GroupResponse

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    _id: PyObjectId
    title: str
    image: Optional[str] = None
    description: Optional[str]
    mentor: Optional[UserResponse] = None
    groups: Optional[List[GroupResponse]] = None
    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    _id: PyObjectId
    title: str
    image: Optional[str] = None
    description: Optional[str]
    mentor: Optional["UserResponse"]
    groups: Optional[List["GroupResponse"]]
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}