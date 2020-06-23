
import os
from json import dumps
from pathlib import Path

from extensions import mgid

# import logging


def test_list_campaigns():
    limit_field = 5
    data: list = mgid.list_campaigns({'limit': limit_field})
    dbg_path = Path(__file__).parent / 'responses' / 'list_campaigns_bot_resp.json'
    dbg_path.write_text(dumps(data))
    assert len(data) == limit_field


if __name__ == "__main__":
    test_list_campaigns()
