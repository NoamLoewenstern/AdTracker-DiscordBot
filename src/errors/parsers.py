from .base import BaseCustomException


class MyArgparseArgumentError(BaseCustomException):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message


class NotExpectedErrorParsing(BaseCustomException):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
