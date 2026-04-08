from typing import Optional, Annotated
from pydantic import BaseModel, BeforeValidator, Field, StringConstraints
from datetime import datetime
from app.domain.enums import TaskPriority, TaskStatus
from app.domain.constants import CONTENT_MAX_LEN, NAME_MAX_LEN


def enure_priority_format(priority: str) -> TaskPriority:
    if priority is None:
        return None
    if not priority:
        raise ValueError("Priority cannot be empty string")
    return TaskPriority(priority.lower())


def ensure_deadline_format(deadline: datetime) -> datetime:
    if deadline is None:
        return None
    if deadline == "":
        raise ValueError("Deadline cannot be empty string")

    raw = str(deadline)
    dt = datetime.fromisoformat(raw)

    if "T" not in raw:
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

    return dt


class TaskCreate(BaseModel):
    name: str = Field(max_length=NAME_MAX_LEN)
    content: str = Field(max_length=CONTENT_MAX_LEN)
    priority: Annotated[TaskPriority, BeforeValidator(enure_priority_format)]
    deadline: Annotated[datetime, BeforeValidator(ensure_deadline_format)]
    project_id: Optional[int] = None
    parent_id: Optional[int] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(max_length=NAME_MAX_LEN, default=None)
    content: Optional[str] = Field(max_length=CONTENT_MAX_LEN, default=None)
    priority: Annotated[Optional[TaskPriority], BeforeValidator(enure_priority_format)] = None
    deadline: Annotated[Optional[datetime], BeforeValidator(ensure_deadline_format)] = None
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


class SearchQuery(BaseModel):
    search: Annotated[Optional[str], StringConstraints(
        min_length=1, 
        max_length=100, 
        strip_whitespace=True, 
        pattern=r'^[^<>\"\\]*$'
        )] = None
