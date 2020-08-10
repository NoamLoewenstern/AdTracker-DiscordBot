import logging
import os

from constants import DEBUG, DEV

logger = logging.getLogger('DISCORD_BOT')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(os.getenv("LOG_FILE", "server.log"))
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | " \
                              # + r"pid:%(process)s module:%(module)s %(message)s",
                              + "%(module)s.py | %(message)s",
                              datefmt=r"%d/%m/%y %H:%M:%S")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
