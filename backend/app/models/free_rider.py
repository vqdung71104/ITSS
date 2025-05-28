from typing import Optional
from datetime import datetime
from beanie import Document, Link
from pydantic import Field

class FreeRider(Document):    
    score: float
    user: Optional[Link["User"]]
    group: Optional[Link["Group"]]
    commit_count: int
    lines_added: int
    lines_removed: int
    files_modified: int
    last_commit_date: datetime

    class Settings:
      name = "free_rider"

from .user_model import User
from .group_model import Group