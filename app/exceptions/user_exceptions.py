from app.exceptions.base_exceptions import BusinessException


class UserException(BusinessException):
    pass


class UserNotFound(UserException):
    MESSAGE = "User not found id='{0}'"
    def __init__(self, id: int) -> None:
            self.message = self.MESSAGE.format(id)
