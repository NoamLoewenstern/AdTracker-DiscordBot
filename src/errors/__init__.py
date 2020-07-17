from .base import BaseCustomException
from .command import InvalidCampaignId, InvalidCommand, InvalidCommandFlag
from .network import APIError, AuthError
from .parsers import MyArgparseArgumentError, NotExpectedErrorParsing
from .platforms import InvalidEmailPassword, InvalidPlatormCampaignName

INTERNAL_ERROR_MSG = {
    "Response": "ERROR",
    "Type": "Internal Error",
}
