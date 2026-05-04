from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.policy import ProjectAssignmentPolicy
from app.repository.project_repository import ProjectRepository
from app.repository.task_repository import TaskRepository
from app.repository.user_repository import UserRepository
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService

def _http_error(status_code: int, code: str, detail: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "detail": detail})

def get_project_repo(db: Session = Depends(get_db))-> ProjectRepository:
    return ProjectRepository(db)

def get_user_repo(db: Session = Depends(get_db))-> UserRepository:
    return UserRepository(db)

def get_task_repo(db: Session = Depends(get_db))-> TaskRepository:
    return TaskRepository(db)

def get_project_assignment_policy(
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> ProjectAssignmentPolicy:
    return ProjectAssignmentPolicy(
        project_repo=project_repo,
        user_repo=user_repo
    )

def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    project_assignment_policy: ProjectAssignmentPolicy = Depends(get_project_assignment_policy),
    ):
    return ProjectService(
        repo=project_repo, 
        user_repo=user_repo,
        project_assignment_policy=project_assignment_policy
        )

def get_user_service(repo: UserRepository = Depends(get_user_repo)):
    return UserService(repo)

def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repo),
    project_assignment_policy: ProjectAssignmentPolicy = Depends(get_project_assignment_policy)
    ):
    return TaskService(
        task_repo=task_repo,
        project_assignment_policy=project_assignment_policy
    )


project_service_dep = Annotated[ProjectService, Depends(get_project_service)]

task_service_dep = Annotated[TaskService, Depends(get_task_service)]

user_service_dep = Annotated[UserService, Depends(get_user_service)]
