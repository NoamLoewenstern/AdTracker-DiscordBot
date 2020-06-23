import os

import config
from services import MGid, ZeroPark

mgid = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'))
zeropark = ZeroPark(os.getenv('ZEROPARK_TOKEN'))
thrive = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'))
