
from .base import BaseCustomException


class APIError(BaseCustomException):
    def __init__(self, platform: str, message='APIError', data: dict = None, explain=''):
        super().__init__(f"{platform}: {message}")
        self.message = message
        self.platform = platform
        self.data = data if data is not None else {}
        self.explain = explain


class AuthError(APIError):
    def __init__(self, platform: str, message='AuthError', data='AUTHENTICATION ERROR', explain=''):
        super().__init__(platform, message, data, explain)
