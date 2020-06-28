
from json import dumps
from pathlib import Path

import pytest

from extensions import thrive
from main import handle_content

TEST_CAMPAING_ID = 1056026

# import logging


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    dbg_path.write_text(data)


@pytest.mark.asyncio
async def test_list_campaigns():
    data = await handle_content('/thrive list')
    log_resp(data, 'list_campaigns_RESP.json')
    assert len(data) >= 0


@pytest.mark.asyncio
async def test_list_sources():
    data = await handle_content(f'/thrive sources {TEST_CAMPAING_ID}')
    log_resp(data, 'list_sources_RESP.json')
    assert len(data) != 0


if __name__ == "__main__":
    test_list_campaigns()
    test_list_sources()
