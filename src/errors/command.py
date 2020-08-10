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


class InvalidCampaignIdError(BaseCustomException):
    def __init__(self, message='Invalid Campaign ID', campaign_id=''):
        super().__init__(f'{message}: {campaign_id}')
        self.message = message
        self.campaign_id = campaign_id
