from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.exceptions.user_exceptions import UserNotFound
from app.models.common import SearchQueryParams
from app.models.users import UserCreate, UserRead, UserUpdate
from app.repository.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix='/users')

def get_user_repo(db: Session = Depends(get_db))-> UserRepository:
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repo)):
    return UserService(repo)

user_service_dep = Annotated[UserService, Depends(get_user_service)]


@router.post("/", response_model=UserRead)
def create_user(params: UserCreate, service: user_service_dep):
    return service.create(params)

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: user_service_dep):
    try:
        return service.get(user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail=f"User not found: {user_id}")


@router.get("/", response_model=List[UserRead])
def get_users(
    service: user_service_dep,
    search_query_params: Annotated[SearchQueryParams, Query()]
):
    return service.list(
        skip=search_query_params.skip,
        limit=search_query_params.limit,
        sort=search_query_params.sort,
        order=search_query_params.order,
        search=search_query_params.search
        )


@router.delete('/{user_id}', status_code=204)
def delete_user(user_id: int, service: user_service_dep):
    """
    Delete project by ID.
    
    Behavior:
    - Hard delete (remove from DB)
    - If user has task assigned: orphan them (user_id = NULL)
    - If user has project assigned: orphan them (user_id = NULL)
    - If user has is project member: orphan them (user_id = NULL)
    - No cascade delete
    
    Status codes:
    - 204: Task deleted
    - 404: Task not found
    """
    try:
        service.delete(user_id)
        return {"detail": "User deleted"}
    except UserNotFound:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, params: UserUpdate, service: user_service_dep):
    """
    Status codes:
    - 404: user_id resource not found
    - 200: user updated succesful
    """
    # Valid task exist
    try:
        user = service.get(user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail=f"User not found: {user_id}")

    return service.update(
        id=user_id,
        params=params
        )
