from beanie import Document
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

class User(Document):
  username: str
  email: EmailStr
  password: str
  created_at: datetime = datetime.utcnow()
  is_active: bool = True

  class Settings:
    collection = "users" 
