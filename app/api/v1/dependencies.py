from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Security
from sqlalchemy.orm import Session

from app.core.auth import oauth2_scheme
from app.db.session import get_db
from app.domain.policy import ProjectAssignmentPolicy
from app.exceptions.user_exceptions import InvalidToken, NotAdminUser, UserNotFound
from app.models.users import UserRead
from app.repository.project_repository import ProjectRepository
from app.repository.task_repository import TaskRepository
from app.repository.user_repository import UserRepository
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService

def _http_error(status_code: int, code: str, detail: str, headers: Optional[dict] = None) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "detail": detail}, headers=headers)

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


def get_current_user(token: Annotated[str, Security(oauth2_scheme)], service: user_service_dep) -> UserRead:
    try:
        return UserRead.model_validate(service.get_user_by_token(token), from_attributes=True)
    except (InvalidToken, UserNotFound) as e:
        raise _http_error(status_code=401, code='authentication_error', detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})


get_current_user_dep = Annotated[UserRead, Depends(get_current_user)]


def get_current_admin_user(token: Annotated[str, Security(oauth2_scheme)], service: user_service_dep) -> UserRead:
    try:
        return UserRead.model_validate(service.get_admin_by_token(token), from_attributes=True)
    except (NotAdminUser) as e:
        raise _http_error(status_code=403, code='authorization_error', detail="Not authorized", headers={"WWW-Authenticate": "Bearer"})
    except (InvalidToken, UserNotFound) as e:
        raise _http_error(status_code=401, code='authentication_error', detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})


get_current_admin_user_dep = Annotated[UserRead, Depends(get_current_admin_user)]
