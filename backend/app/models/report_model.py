from beanie import Document, Link
from datetime import datetime
from typing import Optional
from pydantic import Field

class Report(Document):
    content: str
    student: Optional[Link["User"]]
    task: Optional[Link["Task"]]
    created_at: datetime = Field(default_factory=datetime.now)
    title: Optional[str] = None 
    class Settings:
        collection = "reports"

from .user_model import User
from .task_model import Task