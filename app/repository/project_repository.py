from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.schema import Project
from app.domain.enums import OrderBy, SortBy


class ProjectRepository:
    def __init__(self, db: Session):
        self._db = db
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID from DB"""
        return self._db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(self, skip: int, limit: int, sort: SortBy, order: OrderBy, search: Optional[str]) -> List[Project]:
        """Get all projects from DB"""
        query = self._db.query(Project)
        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))

        try:
            sort_column = getattr(Project, sort.value)
        except AttributeError:
            raise ValueError(f"Invalid sort field: {sort.value}")

        order_by = desc(sort_column) if order == OrderBy.DESC else sort_column

        return query.order_by(order_by).offset(skip).limit(limit).all()
    
    def create(self, project: Project) -> Project:
        """Create new project in DB"""
        self._db.add(project)
        self._db.commit()
        self._db.refresh(project)
        return project
    
    def update(self, project: Project) -> Project:
        """Update existing project in DB"""
        self._db.commit()
        self._db.refresh(project)
        return project
    
    def delete(self, project: Project) -> bool:
        """Delete project from DB"""
        self._db.delete(project)
        self._db.commit()
        return True
