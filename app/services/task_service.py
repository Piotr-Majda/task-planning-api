from typing import List
from sqlalchemy.orm import Session

from app.db.schema import Task, TaskStatus
from app.models.tasks import TaskCreate


class TaskService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def list_task(self)-> List[Task]:
        return self._db.query(Task).all()

    def get_task(self, user_id: int) -> Task | None:
        return self._db.query(Task).filter(Task.id == user_id).first()
    
    def create_task(self, task_create: TaskCreate) -> Task:
        params = task_create.model_dump(exclude_unset=True)
        task = Task(**params, status=TaskStatus.TODO)
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task
    
    def update_task(self, task_id: int, name: str) -> Task | None:
        task = self.get_task(task_id)
        if not task:
            return
        task.name = name
        self._db.commit()
        self._db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        self._db.delete(task)
        self._db.commit()
        return True
