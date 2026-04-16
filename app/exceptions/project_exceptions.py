from app.exceptions.base_exceptions import BusinessException


class ProjectException(BusinessException):
    pass


class ProjectNotFound(ProjectException):
    MESSAGE = "Project not found id='{0}'"
    def __init__(self, id: int) -> None:
        message = self.MESSAGE.format(id)
        super().__init__(message)


class OwnerNotFound(ProjectException):
    MESSAGE = "Owner not found id='{0}'"
    def __init__(self, id: int) -> None:
        message = self.MESSAGE.format(id)
        super().__init__(message)


class MemberNotFound(ProjectException):
    MESSAGE = "Member not found id='{0}'"
    def __init__(self, id: int) -> None:
        message = self.MESSAGE.format(id)
        super().__init__(message)


class ProjectMemberAlreadyExists(ProjectException):
    MESSAGE = f"Project Member with id: '{0}' already exists in project id: '{1}'"
    def __init__(self, project_id: int, user_id: int) -> None:
        message = self.MESSAGE.format(user_id, project_id)
        super().__init__(message)

class MembershipNotFound(ProjectException):
    MESSAGE = "Project membership with user id '{0}' does not exist in project id '{1}'"
    def __init__(self, project_id: int, user_id: int) -> None:
        message = self.MESSAGE.format(user_id, project_id)
        super().__init__(message)
