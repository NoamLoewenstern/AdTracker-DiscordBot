
import pytest

from src.bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp

COMMAND = 'bot-traffic'


@pytest.mark.asyncio
async def test_bot_traffic_list_fields():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 1d --{FIELDS_OPTIONS_FLAG}')
    assert log_resp(data, f'{COMMAND}_list_fields.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_1d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 1d')
    assert log_resp(data, f'{COMMAND}_1d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_3d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 3d')
    assert log_resp(data, f'{COMMAND}_3d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_7d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 7d')
    assert log_resp(data, f'{COMMAND}_7d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_all_campaigns_7d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} 7d')
    assert log_resp(data, f'{COMMAND}_all_campaigns_7d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_all_campaigns_default_d():
    data = await handle_content(f'/{PLATFORM} {COMMAND}')
    assert log_resp(data, f'{COMMAND}_all_campaigns_default-d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_all_campaigns_default_d_ignore_errors():
    data = await handle_content(f'/{PLATFORM} {COMMAND} /ignore-errors')
    assert log_resp(data, f'{COMMAND}_all_campaigns_default-d_ignore-errors.txt')
    assert len(data) != 0
