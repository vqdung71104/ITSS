from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class GroupCreate(BaseModel):
    name: str
    project_id: str
    leader_id: str 

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class GroupResponse(BaseModel):
    id: str
    name: str
    project_id: str
    leader_id: str
    member_ids: List[str]
    task_ids: List[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class GroupListResponse(BaseModel):
    id: str
    name: str
    project_id: str
    leader_id: str
    member_ids: List[str]
    task_ids: List[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}