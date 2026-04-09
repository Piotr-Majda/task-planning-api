from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.domain.constants import NAME_MAX_LEN


class ProjectCreate(BaseModel):
    name: str = Field(max_length=NAME_MAX_LEN)
    owner_id: Optional[int] = None
    task_ids: List[int] = []


class ProjectRead(BaseModel):
    id: int
    name: str
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(max_length=NAME_MAX_LEN, default=None)
    owner_id: Optional[int] = None
