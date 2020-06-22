import os

import config
from services import MGid

mgid = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'))
# todo create zeropark class
zeropark = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'))
