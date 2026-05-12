from typing import Annotated, List
from fastapi import APIRouter, Query
from app.api.v1.dependencies import task_service_dep, _http_error
from app.exceptions.task_exceptions import TaskNotFound
from app.models.common import SearchQueryParams
from app.models.tasks import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks")

@router.get("/", response_model=List[TaskRead])
def get_tasks(
    service: task_service_dep,
    search_query_params: Annotated[SearchQueryParams, Query()]
):
    return service.list(
        skip=search_query_params.skip, 
        limit=search_query_params.limit, 
        sort=search_query_params.sort, 
        order=search_query_params.order, 
        search=search_query_params.search
        )

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, service: task_service_dep):
    try:
        return service.get_task(task_id)
    except TaskNotFound as e:
        raise _http_error(status_code=404, code=e.code, detail=e.message)

@router.post('/', response_model=TaskRead)
def create_task(params: TaskCreate, service: task_service_dep):
    """
    Create task.

    Behavior:
    - New tasks start with status `todo`
    - If `parent_id` is provided, parent task must exist
    - Cannot create a new child task under a parent with status `done`

    Status codes:
    - 200: task created
    - 400: parent_id reference not found
    - 400: parent task is already done
    """
    return service.create_task(params)

@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, params: TaskUpdate, service: task_service_dep):
    """
    Status codes:
    - 404: task_id resource not found
    - 400: parent_id reference not found (bad body)
    - 400: self-parent assignment
    - 400: cycle detected
    - 400: project mismatch
    - 400: parent task cannot be marked done while any child is not done
    - 400: done parent cannot receive a new child task
    - 400: child under done parent cannot be changed back to todo or in_progress
    - 200: task updated successful

    Status behavior:
    - Parent task can be changed to `done` only when all direct children are `done`
    - Done parent can be reopened to `todo` or `in_progress`
    - After reopening parent, child task statuses can be changed again
    """
    try:
        return service.update_task(
            task_id=task_id,
            params=params
            )
    except TaskNotFound as e:
        raise _http_error(status_code=404, code=e.code, detail=e.message)

@router.delete('/{task_id}', status_code=204)
def delete_task(task_id: int, service: task_service_dep):
    """
    Delete task by ID.
    
    Behavior:
    - Hard delete (remove from DB)
    - If task has children: orphan them (parent_id = NULL)
    - No cascade delete
    
    Status codes:
    - 204: Task deleted
    - 404: Task not found
    """
    try:
        service.delete_task(task_id=task_id)
    except TaskNotFound as e:
        raise _http_error(status_code=404, code=e.code, detail=e.message)
