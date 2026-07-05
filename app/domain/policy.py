

from typing import Optional
from app.exceptions.base_exceptions import BusinessException
from app.exceptions.project_exceptions import MemberNotFound, MembershipNotFound, OwnerNotFound, ProjectNotFound
from app.exceptions.user_exceptions import UserNotFound
from app.repository.project_repository import ProjectRepository
from app.repository.user_repository import UserRepository


class ProjectAssignmentPolicy:

    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository) -> None:
        self._project_repo = project_repo
        self._user_repo = user_repo

    def validate_user_exists(self, id: int, not_found_err: Optional[BusinessException]):
        not_found_err = not_found_err if not_found_err is not None else UserNotFound()
        user = self._user_repo.get_by_id(id)
        if user is None:
            raise not_found_err

    def validate_member_exists(self, id: int):
        self.validate_user_exists(id, MemberNotFound(id))

    def validate_owner_exists(self, id: int):
        self.validate_user_exists(id, OwnerNotFound(id))
    
    def validate_project_exists(self, project_id: int):
        project = self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(id=project_id)

    def validate_user_has_membership(self, user_id: int, project_id: int):
        """
        Validate that user has membership in project
        
        Rules:
        - User must exist
        - Project must exist
        - User has membership in Project

        Raises:
            MembershipNotFound if user is not member in project
        """
        membership = self._project_repo.get_member(user_id=user_id, project_id=project_id)
        if membership is None:
            raise MembershipNotFound(project_id=project_id, user_id=user_id)

    def validate_owner_assignment(self, owner_id: Optional[int], project_id: Optional[int]):
        """
        Validate owner assignment if owner and project are present.
        Rules:
        - Owner must exist
        - Project must exist
        - Owner has membership in Project

        Raises:
            OwnerNotFound if owner passed but not exists
            ProjectNotFound if project passed but not exists
            MembershipNotFound if owner is not member in project
        """
        if owner_id is not None:
            self.validate_owner_exists(owner_id)
        if project_id is not None:
            self.validate_project_exists(project_id)
        if owner_id is not None and project_id is not None:
            self.validate_user_has_membership(
                user_id=owner_id, 
                project_id=project_id
                )
