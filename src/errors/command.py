
class InvalidCommand(Exception):
    def __init__(self, message='Invalid Command', command=''):
        super().__init__(message)
        self.command = command


InvalidCommand


class InvalidCampaignId(Exception):
    def __init__(self, message='Invalid Campaign ID', campaign_id=''):
        super().__init__(message)
        self.campaign_id = campaign_id
