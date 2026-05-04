from typing import List, Optional

from app.db.schema import Task, TaskStatus
from app.domain.enums import OrderBy, SortBy
from app.domain.policy import ProjectAssignmentPolicy
from app.exceptions.task_exceptions import CycleDetected, ParentSelfAssignmentDetected, ProjectMismatch, TaskNotFound
from app.models.tasks import TaskCreate, TaskUpdate
from app.repository.task_repository import TaskRepository


class TaskService:
    def __init__(self, task_repo: TaskRepository, project_assignment_policy: ProjectAssignmentPolicy) -> None:
        self._repo = task_repo
        self._project_assignment_policy = project_assignment_policy

    # ════════════════════════════════════════════════════════════
    # CRUD
    # ════════════════════════════════════════════════════════════

    def list(self, skip: int, limit: int, sort: SortBy, order: OrderBy, search: Optional[str])-> List[Task]:
        filters = self._repo.build_filters(search)
        return self._repo.get_all(
            skip=skip, 
            limit=limit, 
            sort_by=sort, 
            order=order, 
            filters=filters
        )

    def get_task(self, task_id: int) -> Task:
        task = self._repo.get_by_id(task_id)
        if not task:
            raise TaskNotFound(id=task_id)
        return task

    def create_task(self, task_create: TaskCreate) -> Task:
        params = task_create.model_dump(exclude_unset=True)
        owner_id = params.get("owner_id")
        project_id = params.get("project_id")
        self._project_assignment_policy.validate_owner_assignment(
            owner_id=owner_id,
            project_id=project_id,
        )
        task = Task(**params, status=TaskStatus.TODO)
        return self._repo.create(task)
    
    def update_task(self, task_id: int, params: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        update_params = params.model_dump(exclude_unset=True)
        project_id = update_params.get('project_id') if 'project_id' in update_params.keys() else task.project_id
        owner_id = update_params.get('owner_id') if 'owner_id' in update_params.keys() else task.owner_id
        self._project_assignment_policy.validate_owner_assignment(owner_id=owner_id, project_id=project_id)
        for name, value in update_params.items():
            setattr(task, name, value)
        
        return self._repo.update(task)

    def delete_task(self, task_id: int) -> None:
        task = self._repo.get_by_id(task_id)
        if not task:
            raise TaskNotFound(id=task_id)
        self._repo.delete(task)

    # ════════════════════════════════════════════════════════════
    # VALIDATORS
    # ════════════════════════════════════════════════════════════

    def validate_self_parent_assignment(self, parent_id: int , task_id: int):
        """
        Validate that parent id is not same as task id.
        
        Rules:
        - Task cannot be assigned as its own parent
        
        Raises:
            ParentSelfAssignmentDetected: if parent and task has same id
        """
        if parent_id == task_id:
            raise ParentSelfAssignmentDetected(
                parent_id=parent_id, 
                task_id=task_id
                )

    def validate_project_consistency(self, parent_project_id: Optional[int], task_project_id: Optional[int]):
        """
        Validate that parent project id is same as task project id to keep consistency
        
        Rules:
        - Task must have same project id as parent
        
        Raises:
            ProjectMismatch: if parent has different project id then task
        """
        if not parent_project_id or not task_project_id:
            return
        
        if parent_project_id != task_project_id:
            raise ProjectMismatch(
                task_project_id=task_project_id, 
                parent_project_id=parent_project_id
                )

    def validate_no_cycle(self, task_id: int, parent_id: int):
        """
        Validate that assigning parent_id as parent doesn't create cycle.
        
        Rules:
        - Task cannot be ancestor of its own parent
        
        Raises:
            CycleDetected: if cycle would be created
        """
        current = parent_id

        while current:
            if current == task_id:
                raise CycleDetected(
                    task_id=task_id,
                    parent_id=parent_id
                )
            parent_task = self._repo.get_by_id(current)
            if not parent_task:
                break
            current = parent_task.parent_id

    # ════════════════════════════════════════════════════════════
    # HELPERS
    # ════════════════════════════════════════════════════════════

    def resolve_project_id(self, parent_project_id: Optional[int], task_project_id: Optional[int]) -> Optional[int]:
        """
        Resolve final project_id: inherit from parent if needed.
        
        Rules:
        - If child doesn't specify: inherit from parent
        - If both specified: use parent
        - If neither: None
        
        Returns:
            Final project_id to use
        """
        if parent_project_id:
            return parent_project_id
        return task_project_id
    