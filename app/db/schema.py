from datetime import datetime
from typing import Annotated, List
from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from app.core.config import TaskPriority, TaskStatus

NameAttr = Annotated[str, mapped_column(String(30), nullable=False)]
IdAttr = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[IdAttr]
    name: Mapped[NameAttr]
    content: Mapped[str] = mapped_column(String(500))
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, name='task_status'))
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority, name='task_priority'))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('tasks.id'), nullable=True)
    parent: Mapped["Task"] = relationship(
        "Task", 
        remote_side="Task.id", 
        back_populates='children'
    )
    children: Mapped[List["Task"]] = relationship(
        "Task", 
        back_populates='parent',
    )
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True)
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates='tasks'
    )
    deadline: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[IdAttr]
    name: Mapped[NameAttr]
    owner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    owner: Mapped["User"] = relationship(
        'User', 
        back_populates='projects'
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task", 
        back_populates='project'
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'
    id: Mapped[IdAttr]
    name: Mapped[NameAttr]
    projects: Mapped[List["Project"]] = relationship(
        'Project', 
        back_populates='owner'
    )


class ProjectMember(Base):
    __tablename__ = 'project_member'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), primary_key=True)
