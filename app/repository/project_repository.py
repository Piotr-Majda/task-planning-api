from typing import Optional, Type

from sqlalchemy.orm import Session

from app.db.schema import Project
from app.repository.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def build_filters(self, search: Optional[str]):
        filters = []
        if search:
            filters.append(Project.name.ilike(f"%{search}%"))
        return filters
