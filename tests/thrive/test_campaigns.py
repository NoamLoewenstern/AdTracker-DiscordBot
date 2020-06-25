
from json import dumps
from pathlib import Path

from extensions import thrive

# import logging


def test_list_campaigns():
    data: list = thrive.list_campaigns()
    dbg_path = Path(__file__).parent / 'responses' / 'list_campaigns_bot_resp.json'
    dbg_path.write_text(dumps(data))
    assert len(data) > 0


def test_list_sources():
    data: list = thrive.list_sources()
    dbg_path = Path(__file__).parent / 'responses' / 'list_campaigns_bot_resp.json'
    dbg_path.write_text(dumps(data))
    assert len(data) > 0


if __name__ == "__main__":
    test_list_campaigns()
    test_list_sources()
