from .base import BaseCustomException


class InvalidPlatormCampaignName(BaseCustomException):
    def __init__(self, platform: str, message='Invalid Platorm Campaign Name', data=''):
        super().__init__(message)
        self.platform = platform
        self.data = data

class InvalidEmailPassword(BaseCustomException):
    def __init__(self, platform: str, message='Invalid Email Password', data=''):
        super().__init__(message)
        self.platform = platform
        self.data = data
