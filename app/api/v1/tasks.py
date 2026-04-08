from typing import Annotated, List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.domain.enums import OrderBy, SortBy
from app.exceptions.task_exceptions import TaskNotFound
from app.models.tasks import SearchQuery, TaskCreate, TaskRead, TaskUpdate
from app.repository.task_repository import TaskRepository
from app.services.task_service import TaskService

router = APIRouter()

def get_task_repo(db: Session = Depends(get_db))-> TaskRepository:
    return TaskRepository(db)

def get_task_service(task_repo: TaskRepository = Depends(get_task_repo)):
    return TaskService(task_repo)

task_service_dep = Annotated[TaskService, Depends(get_task_service)]


@router.get("/tasks/", response_model=List[TaskRead])
def get_tasks(
    service: task_service_dep,
    search: Optional[str] = Query(None, description="String that contains in task name"),
    sort: SortBy = Query(SortBy.NAME, description="Attr on which you want to sort by"),
    order: OrderBy = Query(OrderBy.ASC, description="Sort by this order ascending or descending"),
    page: int = Query(1, ge=1, description="Page number"), 
    limit: int = Query(10, ge=1, le=100, description="Tasks per page"),
):
    skip = (page - 1) * limit

    # walidacja i czyszczenie inputu
    if search is not None:
        search = SearchQuery(search=search).search

    return service.list_task(skip=skip, limit=limit, sort=sort, order=order, search=search)

@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, service: task_service_dep):
    try:
        return service.get_task(task_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

@router.post('/tasks/', response_model=TaskRead)
def create_task(params: TaskCreate, service: task_service_dep):
    parent_id = params.parent_id
    
    if parent_id:
        try:
            parent_task = service.get_task(parent_id)
        except TaskNotFound:
            raise HTTPException(status_code=400, detail=f"Reference parent task not found: {parent_id}")
        service.validate_project_consistency(
            parent_project_id=parent_task.project_id, 
            task_project_id=params.project_id
            )
        params.project_id = service.resolve_project_id(
            parent_project_id=parent_task.project_id, 
            task_project_id=params.project_id
            )
    
    return service.create_task(params)

@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, params: TaskUpdate, service: task_service_dep):
    """
    Update task.
    
    Status codes:
    - 404: task_id resource not found
    - 400: parent_id reference not found (bad body)
    - 400: self-parent assignment
    - 400: cycle detected
    - 400: project mismatch
    """
    # Valid task exist
    try:
        task = service.get_task(task_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    parent_id = params.parent_id
    
    if parent_id:
        service.validate_self_parent_assignment(
            parent_id=parent_id, 
            task_id=task_id
            )

        try:
            parent_task = service.get_task(parent_id)
        except TaskNotFound:
            raise HTTPException(status_code=400, detail=f"Reference parent task not found: {parent_id}")
        service.validate_project_consistency(
            parent_project_id=parent_task.project_id, 
            task_project_id=params.project_id
            )
        params.project_id = service.resolve_project_id(
            parent_project_id=parent_task.project_id, 
            task_project_id=params.project_id
            )
        service.validate_no_cycle(
            task_id=task_id, 
            parent_id=parent_id
            )

    return service.update_task(
        task_id=task_id,
        params=params
        )

@router.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: int, service: task_service_dep):
    if service.delete_task(task_id=task_id):
        return {"detail": "Task deleted"}
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
