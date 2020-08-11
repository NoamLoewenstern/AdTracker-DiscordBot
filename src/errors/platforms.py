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


class InvalidCampaignIDError(InvalidPlatormCampaignNameError):
    def __init__(self, campaign_id: str, platform: str = '', message='Invalid Campaign ID'):
        super().__init__(platform, message)
        self.campaign_id = campaign_id


class InvalidEmailPasswordError(BaseCustomException):
    def __init__(self, platform: str, message='Invalid Email Password', data=None):
        super().__init__(platform, message, data)
        self.platform = platform
        self.data = data
