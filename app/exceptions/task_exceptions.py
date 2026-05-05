

from app.exceptions.base_exceptions import BusinessException


class TaskException(BusinessException):
    pass


class TaskNotFound(TaskException):
    MESSAGE = "Task not found id='{0}'"
    def __init__(self, id: int) -> None:
        message = self.MESSAGE.format(id)
        super().__init__(message)


class ReferenceParentTaskNotFound(TaskException):
    MESSAGE = "Reference parent task not found id='{0}'"
    def __init__(self, id: int) -> None:
        message = self.MESSAGE.format(id)
        super().__init__(message)


class ParentSelfAssignmentDetected(TaskException):
    MESSAGE = "Parent self assignment detected parent_id='{0}' task_id='{1}'"
    def __init__(self, parent_id: int, task_id: int) -> None:
        message = self.MESSAGE.format(parent_id, task_id)
        super().__init__(message)


class ProjectMismatch(TaskException):
    MESSAGE = "Child project {0} doesn't match parent project {1}"
    def __init__(self, task_project_id: int, parent_project_id: int) -> None:
        message = self.MESSAGE.format(task_project_id, parent_project_id)
        super().__init__(message)


class CycleDetected(TaskException):
    MESSAGE = "Cycle detected: task {0} is ancestor of {1}"
    def __init__(self, task_id: int, parent_id: int) -> None:
        message = self.MESSAGE.format(task_id, parent_id)
        super().__init__(message)
