from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.domain.constants import NAME_MAX_LEN


class ProjectCreate(BaseModel):
    name: str = Field(max_length=NAME_MAX_LEN)
    owner_id: Optional[int] = None


class ProjectRead(BaseModel):
    id: int
    name: str
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(max_length=NAME_MAX_LEN, default=None)
    owner_id: Optional[int] = None


class ProjectMemberCreate(BaseModel):
    user_id: int


class ProjectMemberRead(BaseModel):
    user_id: int
    project_id: int
