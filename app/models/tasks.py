from typing import Optional, Annotated
from pydantic import BaseModel, BeforeValidator, Field
from datetime import datetime
from app.domain.enums import TaskPriority, TaskStatus
from app.domain.constants import CONTENT_MAX_LEN, NAME_MAX_LEN


def enure_priority_format(priority: str) -> TaskPriority:
    if priority is None:
        return None
    if not priority:
        raise ValueError("Priority cannot be empty string")
    return TaskPriority(priority.lower())


class TaskCreate(BaseModel):
    name: str = Field(max_length=NAME_MAX_LEN)
    content: str = Field(max_length=CONTENT_MAX_LEN)
    priority: Annotated[TaskPriority, BeforeValidator(enure_priority_format)]
    deadline: datetime
    project_id: Optional[int] = None
    parent_id: Optional[int] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(max_length=NAME_MAX_LEN, default=None)
    content: Optional[str] = Field(max_length=CONTENT_MAX_LEN, default=None)
    priority: Annotated[Optional[TaskPriority], BeforeValidator(enure_priority_format)] = None
    deadline: Optional[datetime] = None
    project_id: Optional[int] = None
    parent_id: Optional[int] = None


class TaskRead(BaseModel):
    id: int
    name: str
    content: str
    priority: TaskPriority
    status: TaskStatus
    deadline: datetime
    project_id: Optional[int] = None
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
