from .base import BaseCustomException


class MyArgparseArgumentError(BaseCustomException):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotExpectedErrorParsingError(MyArgparseArgumentError):
    pass


class InvalidResponseFormatTypeError(BaseCustomException):
    def __init__(self, message: str = 'Invalid Response Format Types.'):
        super().__init__(message)
        self.message = message


class PydanticParseObjError(BaseCustomException):
    def __init__(self, message: str = 'Response Parse not Recognized', data=''):
        super().__init__(message, data)
        self.message = message
        self.data = data
