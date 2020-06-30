
class InvalidPlatormCampaignName(Exception):
    def __init__(self, platform: str, message='Invalid Platorm Campaign Name', data=''):
        super().__init__(message)
        self.platform = platform
        self.data = data
