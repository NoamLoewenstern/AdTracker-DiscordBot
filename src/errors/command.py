from .base import BaseCustomException


class InvalidCommandError(BaseCustomException):
    def __init__(self, message='Invalid Command', command=''):
        super().__init__(f'{message}: "{command}"')
        self.message = message
        self.command = command


class InvalidCommandFlagError(BaseCustomException):
    def __init__(self, message='Invalid Command Flags', flag=''):
        super().__init__(f'{message}: {flag}')
        self.message = message
        self.flag = flag
