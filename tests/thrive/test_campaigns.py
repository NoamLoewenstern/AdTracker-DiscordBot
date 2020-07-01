
from json import dumps
from pathlib import Path

import pytest

from main import handle_content

TEST_CAMPAING_ID = 1056026

# import logging
PLATFORM = 'thrive'


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    dbg_path.write_text(data)


@pytest.mark.asyncio
async def test_list_campaigns():
    data = await handle_content(f'/{PLATFORM} list')
    log_resp(data, 'list_campaigns_RESP.txt')
    assert len(data) >= 0


@pytest.mark.asyncio
async def test_list_sources():
    data = await handle_content(f'/{PLATFORM} sources {TEST_CAMPAING_ID}')
    log_resp(data, 'list_sources_RESP.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_campaigns():
    TEST_CAMPAING_ID = 10013
    data = await handle_content(f'/{PLATFORM} stats {TEST_CAMPAING_ID}')
    log_resp(data, 'stats_campaigns.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_stats_campaigns_all():
    data = await handle_content(f'/{PLATFORM} stats')
    log_resp(data, 'stats_campaigns_all.txt')
    assert len(data) > 0
