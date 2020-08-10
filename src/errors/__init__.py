from .base import BaseCustomException, InternalError
from .command import (InvalidCampaignIdError, InvalidCommandError,
                      InvalidCommandFlagError)
from .network import APIError, AuthError
from .parsers import (InvalidResponseFormatTypeError, MyArgparseArgumentError,
                      NotExpectedErrorParsingError, PydanticParseObjError)
from .platforms import (CampaignNameMissingTrackerIDError,
                        InvalidEmailPasswordError,
                        InvalidPlatormCampaignNameError)


class ErrorList(list):
    pass


class ErrorDict(dict):
    pass
