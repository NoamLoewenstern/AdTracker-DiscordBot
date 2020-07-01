from .base import BaseCustomException


class InvalidCommand(BaseCustomException):
    def __init__(self, message='Invalid Command', command=''):
        super().__init__(message)
        self.message = message
        self.command = command

    def dict(self):
        return {
            'message':  self.message,
            'command':  self.command,
        }


class InvalidCampaignId(BaseCustomException):
    def __init__(self, message='Invalid Campaign ID', campaign_id=''):
        super().__init__(message)
        self.message = message
        self.campaign_id = campaign_id

    def dict(self):
        return {
            'message':  self.message,
            'campaign_id':  self.campaign_id,
        }
