from typing import List, Optional

from app.db.schema import Task, TaskStatus
from app.exceptions.task_exceptions import CycleDetected, ParentSelfAssignmentDetected, ProjectMismatch, TaskNotFound
from app.models.tasks import TaskCreate, TaskUpdate
from app.repository.task_repository import TaskRepository


class TaskService:
    def __init__(self, task_repo: TaskRepository) -> None:
        self._repo = task_repo

    # ════════════════════════════════════════════════════════════
    # CRUD
    # ════════════════════════════════════════════════════════════

    def list_task(self, skip: int, limit: int)-> List[Task]:
        return self._repo.get_all(skip, limit)

    def get_task(self, task_id: int) -> Task:
        task = self._repo.get_by_id(task_id)
        if not task:
            raise TaskNotFound(id=task_id)
        return task

    def create_task(self, task_create: TaskCreate) -> Task:
        params = task_create.model_dump(exclude_unset=True)
        task = Task(**params, status=TaskStatus.TODO)
        return self._repo.create(task)
    
    def update_task(self, task_id: int, params: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        update_params = params.model_dump(exclude_none=True)
        for name, value in update_params.items():
            setattr(task, name, value)
        
        return self._repo.update(task)

    def delete_task(self, task_id: int) -> bool:
        task = self._repo.get_by_id(task_id)
        if not task:
            return False
        return self._repo.delete(task)

    # ════════════════════════════════════════════════════════════
    # VALIDATORS
    # ════════════════════════════════════════════════════════════

    def validate_self_parent_assignment(self, parent_id: int , task_id: int):
        """
        Validate that parent id is not same as task id to not introduse confusion
        
        Rules:
        - Task cannot be self assignemt as parent
        
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
    