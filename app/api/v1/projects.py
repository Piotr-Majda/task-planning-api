from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Query

from app.api.v1.dependencies import project_service_dep
from app.exceptions.project_exceptions import MemberNotFound, ProjectMemberAlreadyExists, ProjectNotFound
from app.models.common import SearchQueryParams
from app.models.projects import NewProjectMember, ProjectCreate, ProjectMemberRead, ProjectRead, ProjectUpdate

router = APIRouter(prefix='/projects')

@router.post("/", response_model=ProjectRead)
def create_project(params: ProjectCreate, service: project_service_dep):
    return service.create(params)

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, service: project_service_dep):
    try:
        return service.get(project_id)
    except ProjectNotFound:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")


@router.get("/", response_model=List[ProjectRead])
def get_projects(
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
def delete_project(project_id: int, service: project_service_dep):
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
        return {"detail": "Project deleted"}
    except ProjectNotFound:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, project_update: ProjectUpdate, service: project_service_dep):
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
    except ProjectNotFound:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")


@router.post("/{project_id}/members", response_model=ProjectMemberRead)
def add_member(project_id:int, new_member: NewProjectMember, service: project_service_dep):
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
            user_id=new_member.user_id
            )
    except (ProjectNotFound, MemberNotFound) as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ProjectMemberAlreadyExists as e:
        raise HTTPException(status_code=409, detail=e.message)

@router.get("/{project_id}/members", response_model=List[ProjectMemberRead])
def get_members(
    project_id: int,
    service: project_service_dep,
):
    try:
        return service.list_members(project_id=project_id)
    except ProjectNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)

# @router.delete('/{project_id}', status_code=204)
# def remove_member(project_id: int, service: project_service_dep):
#     """
#     Delete project by ID.
    
#     Behavior:
#     - Hard delete (remove from DB)
#     - If project has task assigned: orphan them (project_id = NULL)
#     - If project has owner: orphan him
#     - If project has members: orphan them
#     - No cascade delete
    
#     Status codes:
#     - 204: Task deleted
#     - 404: Task not found
#     """
#     try:
#         service.delete(project_id)
#         return {"detail": "Project deleted"}
#     except ProjectNotFound:
#         raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
