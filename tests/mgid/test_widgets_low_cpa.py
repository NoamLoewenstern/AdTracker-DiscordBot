
import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp

COMMAND = 'widgets-low-cpa'
THRESHHOLD = '5'


@pytest.mark.asyncio
async def test_low_cpa_list_fields():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} --{FIELDS_OPTIONS_FLAG}')
    assert log_resp(data, f'{COMMAND}_list_fields.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_low_cpa_widgets():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD}')
    assert log_resp(data, f'{COMMAND}.txt')


@pytest.mark.asyncio
async def test_low_cpa_widgets_3d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 3d')
    assert log_resp(data, f'{COMMAND}_3d.txt')


@pytest.mark.asyncio
async def test_low_cpa_widgets_7days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 7d')
    assert log_resp(data, f'{COMMAND}_7days.txt')


@pytest.mark.asyncio
async def test_low_cpa_widgets_30days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 30d')
    assert log_resp(data, f'{COMMAND}_30days.txt')


@pytest.mark.asyncio
async def test_low_cpa_widgets_90days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 90d')
    assert log_resp(data, f'{COMMAND}_90days.txt')
