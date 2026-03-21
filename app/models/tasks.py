from typing import Optional, Annotated
from pydantic import BaseModel, AfterValidator, BeforeValidator
from datetime import datetime
from app.core.config import TaskPriority, TaskStatus


def enure_priority_format(priority: str) -> TaskPriority:
    return TaskPriority(priority.lower())


class TaskCreate(BaseModel):
    name: str
    content: str
    priority: Annotated[TaskPriority, BeforeValidator(enure_priority_format)]
    deadline: datetime
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
