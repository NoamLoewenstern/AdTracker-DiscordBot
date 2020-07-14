import os

import config
from services import MGid, Thrive, ZeroPark

thrive = Thrive(os.getenv('THRIVE_APIKEY'), os.getenv('THRIVE_INSTALLEDID'))
mgid = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'), thrive)
zeropark = ZeroPark(os.getenv('ZEROPARK_TOKEN'), thrive)
