from enum import Enum

DEFAULT_TIMEOUT_API_REQUEST = 15  # Seconds


class Platforms(str, Enum):
    MGID = 'mgid'
    ZEROPARK = 'zeropark'
    THRIVE = 'thrive'
