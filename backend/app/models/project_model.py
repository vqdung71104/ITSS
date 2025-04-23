from typing import List, Optional
from beanie import Document, Link




class Project(Document):
    title: str
    description: Optional[str]
    mentor: Optional[Link["User"]]
    groups: Optional[List[Link["Group"]]]

    class Settings:
        name = "projects"
        
from .group_model import Group
from .user_model import User