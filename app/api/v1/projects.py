from typing import Annotated, List
from fastapi import APIRouter, Query

from app.api.v1.dependencies import get_current_user_dep, project_service_dep, _http_error
from app.exceptions.project_exceptions import MemberNotFound, MembershipNotFound, ProjectMemberAlreadyExists, ProjectNotFound
from app.models.common import SearchQueryParams
from app.models.projects import ProjectMemberCreate, ProjectCreate, ProjectMemberRead, ProjectRead, ProjectUpdate

router = APIRouter(prefix='/projects')

@router.post("/", response_model=ProjectRead)
def create_project(_current_user: get_current_user_dep, params: ProjectCreate, service: project_service_dep):
    return service.create(params)

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, _current_user: get_current_user_dep, service: project_service_dep):
    try:
        return service.get(project_id)
    except ProjectNotFound as e:
        raise _http_error(404, e.code, e.message)


@router.get("/", response_model=List[ProjectRead])
def get_projects(
    _current_user: get_current_user_dep,
    service: project_service_dep,
    search_query_params: Annotated[SearchQueryParams, Query()]
):
    return service.list(
        skip=search_query_params.skip,
        limit=search_query_params.limit,
        sort=search_query_params.sort,
        order=search_query_params.order,
        search=search_query_params.search
        )

@router.delete('/{project_id}', status_code=204)
def delete_project(project_id: int, _current_user: get_current_user_dep, service: project_service_dep):
    """
    Delete project by ID.

    Behavior:
    - Hard delete (remove from DB)
    - If project has task assigned: orphan them (project_id = NULL)
    - If project has owner: orphan him
    - If project has members: orphan them
    - No cascade delete

    Status codes:
    - 204: Project deleted
    - 404: Project not found
    """
    try:
        service.delete(project_id)
    except ProjectNotFound as e:
        raise _http_error(404, e.code, e.message)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, _current_user: get_current_user_dep, project_update: ProjectUpdate, service: project_service_dep):
    """
    Update project fields.

    Status codes:
    - 200: project updated successfully
    - 404: project resource not found
    """
    try:
        return service.update(
            id=project_id,
            project_update=project_update
            )
    except ProjectNotFound as e:
        raise _http_error(404, e.code, e.message)


@router.post("/{project_id}/members", response_model=ProjectMemberRead)
def add_member(project_id: int, _current_user: get_current_user_dep, member: ProjectMemberCreate, service: project_service_dep):
    """
    Add user as project member.

    Status codes:
    - 200: member added successfully
    - 404: project or user not found
    - 409: user already belongs to the project
    """
    try:
        return service.add_member(
            project_id=project_id,
            user_id=member.user_id
            )
    except (ProjectNotFound, MemberNotFound) as e:
        raise _http_error(404, e.code, e.message)
    except ProjectMemberAlreadyExists as e:
        raise _http_error(409, e.code, e.message)

@router.get("/{project_id}/members", response_model=List[ProjectMemberRead])
def get_members(
    project_id: int,
    _current_user: get_current_user_dep,
    service: project_service_dep,
):
    try:
        return service.list_members(project_id=project_id)
    except ProjectNotFound as e:
        raise _http_error(404, e.code, e.message)

@router.delete('/{project_id}/members/{user_id}', status_code=204)
def remove_membership(project_id: int, user_id: int, _current_user: get_current_user_dep, service: project_service_dep):
    """
    Remove member by user ID.

    Behavior:
    - Hard delete (remove from DB)

    Status codes:
    - 204: membership deleted
    - 404: project or membership not found
    """
    try:
        service.remove_membership(
            project_id=project_id,
            user_id=user_id
            )
    except (ProjectNotFound, MembershipNotFound) as e:
        raise _http_error(404, e.code, e.message)
