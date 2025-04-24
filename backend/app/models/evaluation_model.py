from typing import Optional
from beanie import Document, Link


class Evaluation(Document):
    evaluator: Optional[Link["User"]]
    student: Optional[Link["User"]]
    project: Optional[Link["Project"]]
    score: Optional[float]
    comment: Optional[str]


    class Settings:
        collection = "evaluations"


from .project_model import Project
from .user_model import User
