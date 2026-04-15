from typing import List, Optional, Type

from sqlalchemy.orm import Session

from app.db.schema import Project, ProjectMember
from app.repository.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def build_filters(self, search: Optional[str]):
        filters = []
        if search:
            filters.append(Project.name.ilike(f"%{search}%"))
        return filters

    def add_member(self, project_id: int, user_id: int) -> ProjectMember:
        project_member = ProjectMember(project_id=project_id, user_id=user_id)
        self._db.add(project_member)
        self._db.commit()
        self._db.refresh(project_member)
        return project_member

    def get_member(self, project_id: int, user_id: int) -> ProjectMember | None:
        return self._db.query(ProjectMember).filter(
            ProjectMember.project_id==project_id,
            ProjectMember.user_id==user_id
        ).first()

    def get_all_members(self, project_id: int) -> List[ProjectMember]:
        return self._db.query(ProjectMember).filter(
            ProjectMember.project_id==project_id
        ).order_by(ProjectMember.user_id.asc()).all()
