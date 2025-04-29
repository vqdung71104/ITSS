from datetime import datetime
from typing import Optional, List, Any, Dict
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

class GroupResponse(BaseModel):
    id: str
    name: str

class StudentResponse(BaseModel):
    id: str
    ho_ten: str

class ProjectResponse(BaseModel):
    id: str
    title: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    group_id: PyObjectId
    assigned_student_ids: List[str]
    status: Optional[str] = "pending"
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: PyObjectId
    title: str
    description: Optional[str]
    group: Optional[GroupResponse]
    assigned_students: Optional[List[StudentResponse]]
    status: Optional[str]
    deadline: Optional[datetime]
    related_to_project: Optional[ProjectResponse]

    class Config:
        from_attributes = True