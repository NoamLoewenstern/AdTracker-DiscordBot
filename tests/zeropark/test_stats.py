import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp

TEST_CAMPAING_ID = 'febf1110-a4b2-11ea-bad1-12e5dcaa70ed'
COMMAND = 'stats'


@pytest.mark.asyncio
async def test_stats_list_fields():
    data = await handle_content(f'/{PLATFORM} {COMMAND} --{FIELDS_OPTIONS_FLAG}')
    assert log_resp(data, f'{COMMAND}_list_fields.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details_all_campaigns():
    data = await handle_content(f'/{PLATFORM} {COMMAND}')
    assert log_resp(data, f'{COMMAND}_day_details_all_campaigns.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID}')
    assert log_resp(data, f'{COMMAND}_day_details.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details_3days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 3d')
    assert log_resp(data, f'{COMMAND}_day_details_3days.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details_4days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 4d')
    assert log_resp(data, f'{COMMAND}_day_details_4days.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details_7days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 7d')
    assert log_resp(data, f'{COMMAND}_day_details_7days.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details_30days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 30d')
    assert log_resp(data, f'{COMMAND}_day_details_30days.txt')
    assert len(data) != 0
