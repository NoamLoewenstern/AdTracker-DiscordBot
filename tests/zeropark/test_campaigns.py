
from json import dumps
from pathlib import Path

from extensions import zeropark

# import logging


def test_list_campaigns():
    data: list = zeropark.list_campaigns()
    dbg_path = Path(__file__).parent / 'responses' / 'list_campaigns_bot_resp.json'
    dbg_path.write_text(dumps(data))
    assert len(data) > 0
