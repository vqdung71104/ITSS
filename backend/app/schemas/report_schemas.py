from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from bson import ObjectId
from pydantic_core import core_schema

from schemas.pyobjectid_schemas import PyObjectId

class ReportCreate(BaseModel):
    content: str
    task_id: PyObjectId

    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    _id: PyObjectId
    content: str
    task: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True