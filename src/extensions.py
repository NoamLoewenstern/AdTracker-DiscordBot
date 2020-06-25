import os

import config
from services import MGid, Thrive, ZeroPark

mgid = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'))
zeropark = ZeroPark(os.getenv('ZEROPARK_TOKEN'))
thrive = Thrive(os.getenv('THRIVE_APIKEY'), os.getenv('THRIVE_INSTALLEDID'))
