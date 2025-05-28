from typing import Literal, Optional
from pydantic import BaseModel, EmailStr
from schemas.pyobjectid_schemas import PyObjectId

class UserCreate(BaseModel):
  HoDem: str
  Ten: str
  email: EmailStr
  password: str
  role: Literal["student", "mentor", "admin"]
  github_user: str
  
  class Config:
    from_attributes = True
  
class UserLogin(BaseModel):
  email: EmailStr
  password: str
  class Config:
    from_attributes = True

class UserResponse(BaseModel):
  _id: PyObjectId
  ho_ten: str
  email: EmailStr
  role: str
  class Config:
    from_attributes = True
  
class Token(BaseModel):
  access_token: str
  token_type: str = "bearer"
  class Config:
    from_attributes = True
  
class TokenData(BaseModel):
  email: Optional[str] = "None"
  user_id: Optional[str] = "None"
  class Config:
    from_attributes = True