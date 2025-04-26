from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReportCreate(BaseModel):
    content: str
    task_id: str

class ReportResponse(BaseModel):
    id: str
    content: str
    student: Optional[dict]
    task: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True