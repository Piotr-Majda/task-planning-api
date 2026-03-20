from datetime import datetime, timedelta
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.schema import Task, TaskPriority, TaskStatus


class TaskService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def list_task(self)-> List[Task]:
        return self._db.query(Task).all()

    def get_task(self, user_id: int) -> Task | None:
        return self._db.query(Task).filter(Task.id == user_id).first()
    
    def create_task(self, name: str) -> Task:
        deadline = datetime.now()  + timedelta(days=10)
        task = Task(name=name, content="", status=TaskStatus.TODO, priority=TaskPriority.MINOR, deadline=deadline)
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
