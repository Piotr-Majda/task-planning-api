from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Query


from app.api.v1.dependencies import user_service_dep, _http_error
from app.exceptions.user_exceptions import UserNotFound
from app.models.common import SearchQueryParams
from app.models.users import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix='/users')

@router.post("/", response_model=UserRead)
def create_user(params: UserCreate, service: user_service_dep):
    return service.create(params)

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: user_service_dep):
    try:
        return service.get(user_id)
    except UserNotFound as e:
        raise _http_error(status_code=404, code=e.code, detail=e.message)


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
    except UserNotFound as e:
        raise _http_error(status_code=404, code=e.code, detail=e.message)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, params: UserUpdate, service: user_service_dep):
    """
    Status codes:
    - 404: user_id resource not found
    - 200: user updated successful
    """
    # Valid task exist
    try:
        user = service.get(user_id)
    except UserNotFound as e:
        raise _http_error(status_code=404, code=e.code, detail=e.message)

    return service.update(
        id=user_id,
        params=params
        )
