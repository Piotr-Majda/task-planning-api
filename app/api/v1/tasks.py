from fastapi import APIRouter, Depends
from app.db.schema import SesssionLocal
from app.models.tasks import TaskCreate, TaskRead
from app.services.task_service import TaskService

router = APIRouter()

def get_task_service() -> TaskService:
    return TaskService(session=SesssionLocal())

@router.get('/tasks', response_model=list[TaskRead])
def get_tasks(service: TaskService = Depends[get_task_service]):
    return service.list_task()