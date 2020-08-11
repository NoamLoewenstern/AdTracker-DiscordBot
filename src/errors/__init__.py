from .base import BaseCustomException, InternalError
from .command import InvalidCommandError, InvalidCommandFlagError
from .network import APIError, AuthError
from .parsers import (InvalidResponseFormatTypeError, MyArgparseArgumentError,
                      NotExpectedErrorParsingError, PydanticParseObjError)
from .platforms import (CampaignNameMissingTrackerIDError,
                        InvalidCampaignIDError, InvalidEmailPasswordError,
                        InvalidPlatormCampaignNameError)


class ErrorList(list):
    pass


class ErrorDict(dict):
    pass
