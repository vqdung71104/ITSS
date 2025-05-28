from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from bson import ObjectId
from pydantic_core import core_schema
from schemas.pyobjectid_schemas import PyObjectId
from schemas.user_schemas import UserResponse
from schemas.group_schemas import GroupResponse

class FreeRiderResponse(BaseModel):
    score: float
    user: Optional[UserResponse] = None
    group: Optional[GroupResponse] = None
    commit_count: int
    lines_added: int
    lines_removed: int
    files_modified: int
    last_commit_date: str
    message: Optional[str] = None

    class Config:
      arbitrary_types_allowed = True
      json_encoders = {ObjectId: str}