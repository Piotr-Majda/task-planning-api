from typing import List, Optional

from app.db.schema import Project
from app.domain.enums import OrderBy, SortBy
from app.exceptions.project_exceptions import OwnerNotFound, ProjectNotFound
from app.models.projects import ProjectCreate, ProjectUpdate
from app.repository.project_repository import ProjectRepository
from app.repository.user_repository import UserRepository


class ProjectService:
    def __init__(self, repo: ProjectRepository, user_repo: UserRepository) -> None:
        self._repo = repo
        self._user_repo = user_repo

    # ════════════════════════════════════════════════════════════
    # CRUD
    # ════════════════════════════════════════════════════════════

    def list(self, skip: int, limit: int, sort: SortBy, order: OrderBy, search: Optional[str])-> List[Project]:
        filters = self._repo.build_filters(search)
        return self._repo.get_all(
            skip=skip, 
            limit=limit, 
            sort_by=sort, 
            order=order, 
            filters=filters
        )

    def get(self, id: int) -> Project:
        project = self._repo.get_by_id(id)
        if not project:
            raise ProjectNotFound(id=id)
        return project

    def create(self, project_create: ProjectCreate) -> Project:
        if project_create.owner_id is not None:
            self.validate_owner_assignment(project_create.owner_id)
        params = project_create.model_dump(exclude_unset=True)
        project = Project(**params)
        return self._repo.create(project)
    
    def update(self, id: int, project_update: ProjectUpdate) -> Project:
        if project_update.owner_id is not None:
            self.validate_owner_assignment(project_update.owner_id)
        project = self.get(id)
        params = project_update.model_dump(exclude_unset=True)
        for name, value in params.items():
            setattr(project, name, value)
        
        return self._repo.update(project)

    def delete(self, id: int) -> None:
        project = self._repo.get_by_id(id)
        if not project:
            raise ProjectNotFound(id=id)
        self._repo.delete(project)

    # ════════════════════════════════════════════════════════════
    # VALIDATORS
    # ════════════════════════════════════════════════════════════

    def validate_owner_assignment(self, owner_id: int):
        user = self._user_repo.get_by_id(owner_id)
        if user is None:
            raise OwnerNotFound(owner_id)
