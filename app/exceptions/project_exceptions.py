from app.exceptions.base_exceptions import BusinessException


class ProjectException(BusinessException):
    pass


class ProjectNotFound(ProjectException):
    MESSAGE = "Project not found id='{0}'"
    def __init__(self, id: int) -> None:
            self.message = self.MESSAGE.format(id)
