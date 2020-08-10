import os
from enum import Enum

import logger
from bot.help import CommandHelpDocumentation
from services import MGid, Thrive, ZeroPark

thrive = Thrive(os.getenv('THRIVE_APIKEY'), os.getenv('THRIVE_INSTALLEDID'))
mgid = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'), thrive)
zeropark = ZeroPark(os.getenv('ZEROPARK_TOKEN'), thrive)

helper_docs = CommandHelpDocumentation()


class OutputFormatTypes(str, Enum):
    str = 'str'
    list = 'list'
    json = 'json'
    csv = 'csv'
