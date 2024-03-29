import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp

COMMAND = 'spent'


@pytest.mark.asyncio
async def test_spent_list_fields():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} --{FIELDS_OPTIONS_FLAG}')
    assert log_resp(data, f'{COMMAND}_list_fields.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_spent():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} /fields:id,name,spent')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, f'{COMMAND}.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns():
    data = await handle_content(f'/{PLATFORM} {COMMAND} /fields:id,name,spent')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, f'{COMMAND}_all_campaigns.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns_3d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} /fields:id,name,spent /time_range:3d')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, f'{COMMAND}_all_campaigns_3d.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns_7d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} /fields:id,name,spent /time_range:7d')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, f'{COMMAND}_all_campaigns_7d.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns_30d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} /fields:id,name,spent /time_range:30d')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, f'{COMMAND}_all_campaigns_30d.txt')
    assert len(data) > 0
