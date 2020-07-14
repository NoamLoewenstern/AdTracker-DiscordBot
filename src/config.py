import logging
import os

logging.basicConfig(
    # filename=getenv("SERVICE_LOG", "server.log"),
    level=logging.DEBUG if os.getenv('DEBUG') else logging.info,
    format="%(levelname)s: %(asctime)s" \
    # + r"pid:%(process)s module:%(module)s %(message)s",
    + "| %(module)s.py | %(message)s",
    datefmt=r"%d/%m/%y %H:%M:%S",
)


DEFAULT_OUTPUT_FORMAT = 'list'
DEFAULT_TIME_INTERVAL = '360d'
MAX_URL_PARAMS_SIZE = 500
