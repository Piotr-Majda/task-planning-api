import re

patter = re.compile(r"(?<!^)(?=[A-Z])")

def _camel_to_snake(value: str) -> str:
    return patter.sub("_", value).lower()


class BusinessException(Exception):
    message: str
    code: str

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or _camel_to_snake(self.__class__.__name__)
        self.detail = {'detail': self.message, 'code': self.code}
