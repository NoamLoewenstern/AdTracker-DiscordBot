import os
from enum import Enum

DEFAULT_TIMEOUT_API_REQUEST = 120  # Seconds
DEBUG = os.getenv('DEBUG', False)
DEV = os.getenv('DEV', False)


class Platforms(str, Enum):
    MGID = 'mgid'
    MG = 'mg'
    ZEROPARK = 'zeropark'
    ZP = 'zp'
    THRIVE = 'thrive'
    TRACKER = 'tracker'
