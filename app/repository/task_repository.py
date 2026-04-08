from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.schema import Task
from app.domain.enums import OrderBy, SortBy


class TaskRepository:
    def __init__(self, db: Session):
        self._db = db
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID from DB"""
        return self._db.query(Task).filter(Task.id == task_id).first()
    
    def get_all(self, skip: int, limit: int, sort: SortBy, order: OrderBy, search: Optional[str]) -> List[Task]:
        """Get all tasks from DB"""
        query = self._db.query(Task)
        if search:
            query = query.filter(Task.name.ilike(f"%{search}%"))

        try:
            sort_column = getattr(Task, sort.value)
        except AttributeError:
            raise ValueError(f"Invalid sort field: {sort.value}")

        order_by = desc(sort_column) if order == OrderBy.DESC else sort_column

        return query.order_by(order_by).offset(skip).limit(limit).all()
    
    def create(self, task: Task) -> Task:
        """Create new task in DB"""
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task
    
    def update(self, task: Task) -> Task:
        """Update existing task in DB"""
        self._db.commit()
        self._db.refresh(task)
        return task
    
    def delete(self, task: Task) -> bool:
        """Delete task from DB"""
        self._db.delete(task)
        self._db.commit()
        return True
