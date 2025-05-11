from typing import Optional, List, Dict, Any
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
    _id: PyObjectId
    evaluator: Dict[str, str]  # Dictionary chứa thông tin evaluator
    student: Dict[str, str]    # Dictionary chứa thông tin student
    project: Dict[str, str]    # Dictionary chứa thông tin project
    score: Optional[float]
    comment: Optional[str]

    class Config:
        from_attributes = True