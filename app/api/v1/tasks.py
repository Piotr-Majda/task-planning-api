from typing import Annotated, List
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tasks import TaskCreate, TaskRead
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
def create_task(task_create_param: TaskCreate, service: task_service_dep):
    return service.create_task(task_create_param)

@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, name: Annotated[str, Form], service: task_service_dep):
    return service.update_task(
        task_id=task_id,
        name=name
        )

@router.delete('/tasks/{task_id}')
def delete_task(task_id: int, service: task_service_dep):
    if service.delete_task(task_id=task_id):
        return HTTPException(status_code=204, detail=f"Task with id {task_id} deleted")
    return HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
