from typing import Optional, List, Any
from pydantic import BaseModel
from bson import ObjectId
from pydantic_core import core_schema

# Định nghĩa PyObjectId
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x), when_used="json"
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


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