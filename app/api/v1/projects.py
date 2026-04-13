from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.exceptions.project_exceptions import ProjectNotFound
from app.models.common import SearchQueryParams
from app.models.projects import ProjectCreate, ProjectRead, ProjectUpdate
from app.repository.project_repository import ProjectRepository
from app.services.project_service import ProjectService

router = APIRouter(prefix='/projects')

def get_project_repo(db: Session = Depends(get_db))-> ProjectRepository:
    return ProjectRepository(db)

def get_project_service(task_repo: ProjectRepository = Depends(get_project_repo)):
    return ProjectService(task_repo)

project_service_dep = Annotated[ProjectService, Depends(get_project_service)]


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
    - 204: Task deleted
    - 404: Task not found
    """
    try:
        service.delete(project_id)
        return {"detail": "Project deleted"}
    except ProjectNotFound:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, params: ProjectUpdate, service: project_service_dep):
    """
    Status codes:
    - 404: project_id resource not found
    - 200: project updated succesful
    """
    # Valid task exist
    try:
        task = service.get(project_id)
    except ProjectNotFound:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

    return service.update(
        id=project_id,
        params=params
        )
