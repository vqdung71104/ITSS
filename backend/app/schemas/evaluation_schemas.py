from pydantic import BaseModel
from typing import Optional

class EvaluationCreate(BaseModel):
    student_id: str
    project_id: str
    score: Optional[float] = None
    comment: Optional[str] = None

class EvaluationResponse(BaseModel):
    id: str
    evaluator: Optional[dict]
    student: Optional[dict]
    project: Optional[dict]
    score: Optional[float]
    comment: Optional[str]

    class Config:
        from_attributes = True