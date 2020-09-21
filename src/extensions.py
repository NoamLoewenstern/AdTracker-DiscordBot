import os
from enum import Enum

import logger
from bot.help import CommandHelpDocumentation
from services import MGid, Thrive, ZeroPark
MAX_MGID_ACCOUNTS = 5

thrive = Thrive(os.getenv('THRIVE_APIKEY'), os.getenv('THRIVE_INSTALLEDID'))
mgid_instances = []
for i in range(MAX_MGID_ACCOUNTS):
    mgid_client_id = os.getenv(f'MGID_{i}_CLIENT_ID')
    mgid_token = os.getenv(f'MGID_{i}_TOKEN')
    if mgid_client_id and mgid_token:
        mgid_instances.append(MGid(mgid_client_id, mgid_token, thrive))
mgid = mgid_instances[0]

zeropark = ZeroPark(os.getenv('ZEROPARK_TOKEN'), thrive)

helper_docs = CommandHelpDocumentation()


class OutputFormatTypes(str, Enum):
    str = 'str'
    list = 'list'
    json = 'json'
    csv = 'csv'
