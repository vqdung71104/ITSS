from pydantic import BaseModel
from typing import Optional, List

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    mentor: Optional[dict]  # Trả về thông tin mentor (User)
    groups: Optional[List[dict]]  # Trả về danh sách nhóm

    class Config:
        from_attributes = True