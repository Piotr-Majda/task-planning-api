from datetime import datetime
from email.policy import default
from typing import Annotated, List
from sqlalchemy import Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, MappedColumn, relationship, Mapped, mapped_column
from app.domain.enums import TaskPriority, TaskStatus, UserRole
from app.domain.constants import CONTENT_MAX_LEN, NAME_MAX_LEN

NameAttr = Annotated[str, mapped_column(String(NAME_MAX_LEN), nullable=False)]
IdAttr = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[IdAttr]
    name: Mapped[NameAttr]
    content: Mapped[str] = mapped_column(String(CONTENT_MAX_LEN))
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
    owner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    owner: Mapped["User"] = relationship(
        "User", 
        back_populates='tasks'
    )
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
    id: Mapped[IdAttr] = MappedColumn(Integer, primary_key=True, index=True)
    name: Mapped[NameAttr] = MappedColumn(String(120), unique=True, nullable=False)
    role: Mapped[UserRole] = MappedColumn(Enum(UserRole), name='role', default=UserRole.USER) # TODO tmp to not break tests
    password_hashed: Mapped[String] = MappedColumn(String(200), nullable=False)
    projects: Mapped[List["Project"]] = relationship(
        'Project', 
        back_populates="owner"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="owner"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class ProjectMember(Base):
    __tablename__ = 'project_member'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), primary_key=True)
