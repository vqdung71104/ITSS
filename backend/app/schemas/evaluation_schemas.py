from typing import Optional, List, Any
from pydantic import BaseModel
from bson import ObjectId
from pydantic_core import core_schema
from schemas.pyobjectid_schemas import PyObjectId


class EvaluationCreate(BaseModel):
    student_id: PyObjectId
    project_id: PyObjectId
    score: Optional[float] = None
    comment: Optional[str] = None

class EvaluationResponse(BaseModel):
    id: PyObjectId
    evaluator: Optional[dict]
    student: Optional[dict]
    project: Optional[dict]
    score: Optional[float]
    comment: Optional[str]

    class Config:
        from_attributes = True