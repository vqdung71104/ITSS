from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from bson import ObjectId
from pydantic_core import core_schema

from schemas.pyobjectid_schemas import PyObjectId

class ReportCreate(BaseModel):
    content: str
    task_id: PyObjectId

class ReportResponse(BaseModel):
    id: PyObjectId
    content: str
    student: Optional[dict]
    task: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True