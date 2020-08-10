from .base import BaseCustomException


class InvalidPlatormCampaignNameError(BaseCustomException):
    def __init__(self, platform: str, message='Invalid Platform Campaign Name', data=None):
        super().__init__(platform, message, data)
        self.message = message
        self.platform = platform
        self.data = data


class CampaignNameMissingTrackerIDError(InvalidPlatormCampaignNameError):
    def __init__(self, id: str, name: str, platform: str = '', message='Campaign Name Missing Tracker ID Reference'):
        super().__init__(platform, message)
        self.id = id
        self.name = name


class InvalidEmailPasswordError(BaseCustomException):
    def __init__(self, platform: str, message='Invalid Email Password', data=None):
        super().__init__(platform, message, data)
        self.platform = platform
        self.data = data
