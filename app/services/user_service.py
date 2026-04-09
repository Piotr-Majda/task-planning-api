from typing import List, Optional

from app.db.schema import Project, User
from app.domain.enums import OrderBy, SortBy
from app.exceptions.project_exceptions import ProjectNotFound
from app.exceptions.user_exceptions import UserNotFound
from app.models.projects import ProjectCreate, ProjectUpdate
from app.repository.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    # ════════════════════════════════════════════════════════════
    # CRUD
    # ════════════════════════════════════════════════════════════

    def list(self, skip: int, limit: int, sort: SortBy, order: OrderBy, search: Optional[str])-> List[User]:
        filters = self._repo.build_filters(search)
        return self._repo.get_all(
            skip=skip, 
            limit=limit, 
            sort_by=sort, 
            order=order, 
            filters=filters
        )

    def get(self, id: int) -> User:
        user = self._repo.get_by_id(id)
        if not user:
            raise UserNotFound(id=id)
        return user

    def create(self, project_create: ProjectCreate) -> User:
        params = project_create.model_dump(exclude_unset=True)
        user = User(**params)
        return self._repo.create(user)
    
    def update(self, id: int, params: ProjectUpdate) -> User:
        user = self.get(id)
        update_params = params.model_dump(exclude_none=True)
        for name, value in update_params.items():
            setattr(user, name, value)
        
        return self._repo.update(user)

    def delete(self, id: int) -> None:
        project = self._repo.get_by_id(id)
        if not project:
            raise UserNotFound(id=id)
        self._repo.delete(project)
