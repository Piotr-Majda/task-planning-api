from typing import List, Optional

from app.db.schema import Project
from app.domain.enums import OrderBy, SortBy
from app.exceptions.project_exceptions import ProjectNotFound
from app.models.projects import ProjectCreate, ProjectUpdate
from app.repository.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, repo: ProjectRepository) -> None:
        self._repo = repo

    # ════════════════════════════════════════════════════════════
    # CRUD
    # ════════════════════════════════════════════════════════════

    def list(self, skip: int, limit: int, sort: SortBy, order:OrderBy, search: Optional[str])-> List[Project]:
        return self._repo.get_all(skip, limit, sort, order, search)

    def get(self, id: int) -> Project:
        project = self._repo.get_by_id(id)
        if not project:
            raise ProjectNotFound(id=id)
        return project

    def create(self, project_create: ProjectCreate) -> Project:
        params = project_create.model_dump(exclude_unset=True)
        project = Project(**params)
        return self._repo.create(project)
    
    def update(self, id: int, params: ProjectUpdate) -> Project:
        project = self.get(id)
        update_params = params.model_dump(exclude_none=True)
        for name, value in update_params.items():
            setattr(project, name, value)
        
        return self._repo.update(project)

    def delete(self, id: int) -> bool:
        project = self._repo.get_by_id(id)
        if not project:
            return False
        return self._repo.delete(project)
