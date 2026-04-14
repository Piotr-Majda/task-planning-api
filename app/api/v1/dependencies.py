from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.project_repository import ProjectRepository
from app.repository.task_repository import TaskRepository
from app.repository.user_repository import UserRepository
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService

router = APIRouter(prefix='/projects')

def get_project_repo(db: Session = Depends(get_db))-> ProjectRepository:
    return ProjectRepository(db)

def get_user_repo(db: Session = Depends(get_db))-> UserRepository:
    return UserRepository(db)

def get_task_repo(db: Session = Depends(get_db))-> TaskRepository:
    return TaskRepository(db)

def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    ):
    return ProjectService(
        repo=project_repo, 
        user_repo=user_repo
        )

def get_user_service(repo: UserRepository = Depends(get_user_repo)):
    return UserService(repo)

def get_task_service(task_repo: TaskRepository = Depends(get_task_repo)):
    return TaskService(task_repo)


project_service_dep = Annotated[ProjectService, Depends(get_project_service)]

task_service_dep = Annotated[TaskService, Depends(get_task_service)]

user_service_dep = Annotated[UserService, Depends(get_user_service)]
