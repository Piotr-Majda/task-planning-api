from app.exceptions.base_exceptions import BusinessException


class UserException(BusinessException):
    pass


class UserNotFound(UserException):
    MESSAGE = "User not found"
    def __init__(self) -> None:
        message = self.MESSAGE
        super().__init__(message)

class NotAdminUser(UserNotFound):
    MESSAGE = "User not has admin permision"

class InvalidPassword(UserException):
    MESSAGE = "Password invalid"
    def __init__(self) -> None:
        message = self.MESSAGE
        super().__init__(message)

class InvalidToken(UserException):
    MESSAGE = "Token is invalid or expired"
    def __init__(self) -> None:
        message = self.MESSAGE
        super().__init__(message)
