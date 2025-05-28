from datetime import datetime
from typing import Optional
from beanie import Document, Link
from pydantic import Field


class Evaluation(Document):
    evaluator: Optional[Link["User"]]
    student: Optional[Link["User"]]
    project: Optional[Link["Project"]]
    score: Optional[float]
    comment: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        collection = "evaluations"


from .project_model import Project
from .user_model import User
