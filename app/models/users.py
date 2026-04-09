from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.domain.constants import NAME_MAX_LEN


class UserCreate(BaseModel):
    name: str = Field(max_length=NAME_MAX_LEN)


class UserRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = Field(max_length=NAME_MAX_LEN, default=None)
