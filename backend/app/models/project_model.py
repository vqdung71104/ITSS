from typing import List, Optional
from beanie import Document, Link

class Project(Document):
    title: str
    description: Optional[str]
    mentor: Optional[Link["User"]]
    groups: Optional[List[Link["Group"]]]
    image: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Project Title",
                "description": "Project Description",
                "mentor": "Mentor ID",
                "groups": ["Group ID 1", "Group ID 2"],
                "image": "Image URL"
            }
        }

    class Settings:
        collection = "projects"
        
from .group_model import Group
from .user_model import User