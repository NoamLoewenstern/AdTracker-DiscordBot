import socket

from utils.helpers import is_valid_uuid4

HOSTNAME = socket.gethostname()
RUNNING_ON_SERVER = is_valid_uuid4(HOSTNAME)
DEFAULT_OUTPUT_FORMAT = 'list'
DEFAULT_TIME_INTERVAL = '360d'
MAX_URL_PARAMS_SIZE = 500
DEFAULT_ALL_CAMPAIGNS_ALIAS = 'all'
DEBUG_COMMAND_FLAG = '--debug'
DEFAULT_FILTER_NUMBER = 5
