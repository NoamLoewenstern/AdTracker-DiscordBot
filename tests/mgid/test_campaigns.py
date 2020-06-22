
import os
from json import dumps
from pathlib import Path

from services import MGid

# import logging


def test_list_campaigns():
    limit_field = 5
    dbg_path = Path(__file__).parent / 'responses' / 'list_campaigns_latest.json'
    mgid = MGid(os.getenv('MGID_CLIENT_ID'), os.getenv('MGID_TOKEN'))
    data: list = mgid.list_campaigns({'limit': limit_field})
    dbg_path.write_text(dumps(data))
    assert len(data) == limit_field


if __name__ == "__main__":
    test_list_campaigns()
