from beanie import Document, Link
from pydantic import EmailStr
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

    class Settings:
        collection = "users"

from .group_model import Group
from .task_model import Task
