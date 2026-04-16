from typing import List, Optional

from app.db.schema import Project, ProjectMember, User
from app.domain.enums import OrderBy, SortBy
from app.exceptions.project_exceptions import MemberNotFound, MembershipNotFound, ProjectMemberAlreadyExists, OwnerNotFound, ProjectNotFound
from app.models.projects import ProjectCreate, ProjectUpdate
from app.repository.project_repository import ProjectRepository
from app.repository.user_repository import UserRepository


class ProjectService:
    def __init__(self, repo: ProjectRepository, user_repo: UserRepository) -> None:
        self._project_repo = repo
        self._user_repo = user_repo

    # ════════════════════════════════════════════════════════════
    # CRUD
    # ════════════════════════════════════════════════════════════

    def list(self, skip: int, limit: int, sort: SortBy, order: OrderBy, search: Optional[str])-> List[Project]:
        filters = self._project_repo.build_filters(search)
        return self._project_repo.get_all(
            skip=skip, 
            limit=limit, 
            sort_by=sort, 
            order=order, 
            filters=filters
        )

    def get(self, id: int) -> Project:
        project = self._project_repo.get_by_id(id)
        if not project:
            raise ProjectNotFound(id=id)
        return project

    def create(self, project_create: ProjectCreate) -> Project:
        if project_create.owner_id is not None:
            self.validate_owner_exists(project_create.owner_id)
        params = project_create.model_dump(exclude_unset=True)
        project = Project(**params)
        return self._project_repo.create(project)
    
    def update(self, id: int, project_update: ProjectUpdate) -> Project:
        if project_update.owner_id is not None:
            self.validate_owner_exists(project_update.owner_id)
        project = self.get(id)
        params = project_update.model_dump(exclude_unset=True)
        for name, value in params.items():
            setattr(project, name, value)
        
        return self._project_repo.update(project)

    def delete(self, id: int) -> None:
        project = self._project_repo.get_by_id(id)
        if not project:
            raise ProjectNotFound(id=id)
        self._project_repo.delete(project)

    # ════════════════════════════════════════════════════════════
    # VALIDATORS
    # ════════════════════════════════════════════════════════════

    def validate_owner_exists(self, id: int):
        entity: User | None = self._user_repo.get_by_id(id)
        if entity is None:
            raise OwnerNotFound(id)

    def validate_member_exists(self, id: int):
        entity = self._user_repo.get_by_id(id)
        if entity is None:
            raise MemberNotFound(id)
    
    def validate_project_exists(self, id: int):
        entity = self._project_repo.get_by_id(id)
        if entity is None:
            raise ProjectNotFound(id)

    def validate_membership_in_project(self, project_id: int, user_id: int):
        entity = self._project_repo.get_member(project_id, user_id)
        if entity is None:
            raise MembershipNotFound(
                project_id=project_id, 
                user_id=user_id
                )

    # ════════════════════════════════════════════════════════════
    # MEMBERS
    # ════════════════════════════════════════════════════════════

    def add_member(self, project_id: int, user_id: int) -> ProjectMember:
        self.validate_project_exists(project_id)
        self.validate_member_exists(user_id)
        member = self._project_repo.get_member(
            project_id=project_id, 
            user_id=user_id
            )
        if member:
            raise ProjectMemberAlreadyExists(project_id=project_id, user_id=user_id)
        return self._project_repo.add_member(
            project_id=project_id, 
            user_id=user_id
            )

    def list_members(self, project_id: int) -> List[ProjectMember]:
        self.validate_project_exists(project_id)
        return self._project_repo.get_all_members(project_id=project_id)

    def remove_membership(self, project_id: int, user_id: int):
        self.validate_project_exists(project_id)
        self.validate_membership_in_project(project_id=project_id, user_id=user_id)
        self._project_repo.remove_membership(
            project_id=project_id,
            user_id=user_id
            )
