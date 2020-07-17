import os
from enum import Enum

DEFAULT_TIMEOUT_API_REQUEST = 30  # Seconds
DEBUG = os.getenv('DEBUG', False)
DEV = os.getenv('DEV', False)

class Platforms(str, Enum):
    MGID = 'mgid'
    ZEROPARK = 'zeropark'
    THRIVE = 'thrive'
