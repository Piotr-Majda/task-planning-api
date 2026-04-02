from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tasks import TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


def get_task_service(db: Session = Depends(get_db)):
    return TaskService(db)

task_service_dep = Annotated[TaskService, Depends(get_task_service)]

@router.get("/tasks/", response_model=List[TaskRead])
def get_tasks(service:  task_service_dep):
    return service.list_task()

@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, service: task_service_dep):
    return service.get_task(task_id)

@router.post('/tasks/', response_model=TaskRead)
def create_task(params: TaskCreate, service: task_service_dep):
    if params.parent_id:
        parent_task = service.get_task(params.parent_id)
        if not parent_task:
            raise HTTPException(status_code=404, detail=f'Task with id {params.parent_id}')
        
        if parent_task.project_id and not params.project_id:
            params.project_id = parent_task.project_id
        elif parent_task.project_id != params.project_id:
            raise HTTPException(status_code=400, detail=f"Project id: '{params.project_id}' is not consistent parent task")
    
    return service.create_task(params)

@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, params: TaskUpdate, service: task_service_dep):
    # Valid task exist
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    parent_id = params.parent_id
    # Valid self parent
    if parent_id and parent_id == task_id:
        raise HTTPException(status_code=400, detail=f"Change parent id to self is not allowed")
    
    elif parent_id:
        parent_task = service.get_task(parent_id)
        if not parent_task:
            raise HTTPException(status_code=404, detail=f'Cant change to parent id {parent_id}, this task not exist')
        
        if parent_task.project_id and not params.project_id:
            params.project_id = parent_task.project_id
        elif parent_task.project_id != params.project_id:
            raise HTTPException(status_code=400, detail=f"Project id: '{params.project_id}' is not consistent parent task")
    
        # detect cycle in parent tree
        curr = parent_task.id
        task =  parent_task

        while task:
            if task.parent_id == task_id:
                raise HTTPException(status_code=400, detail=f"Cycle detected cannot assing parent with id: {params.parent_id}")
            curr = task.parent_id
            if not curr:
                break
            task = service.get_task(curr)

    return service.update_task(
        task_id=task_id,
        params=params
        )

@router.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: int, service: task_service_dep):
    if service.delete_task(task_id=task_id):
        return {"detail": "Task deleted"}
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
