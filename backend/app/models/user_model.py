from datetime import datetime
from beanie import Document, Link
from pydantic import EmailStr, Field
from typing import List, Optional


class User(Document):
    HoDem: str
    Ten: str
    email: EmailStr
    password: str
    role: str
    group_id: Optional[Link["Group"]] 
    tasks: Optional[List[Link["Task"]]]
    contributions: Optional[str]
    ho_ten: Optional[str] = None
    github_user: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        collection = "users"

from .group_model import Group
from .task_model import Task
