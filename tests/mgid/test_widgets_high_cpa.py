
import pytest

from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp

COMMAND = 'widgets-high-cpa'
THRESHHOLD = '5'


@pytest.mark.asyncio
async def test_high_cpa_widgets():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD}')
    assert log_resp(data, f'{COMMAND}.txt')


@pytest.mark.asyncio
async def test_high_cpa_widgets_3d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 3d')
    assert log_resp(data, f'{COMMAND}_3d.txt')


@pytest.mark.asyncio
async def test_high_cpa_widgets_7days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 7d')
    assert log_resp(data, f'{COMMAND}_7days.txt')


@pytest.mark.asyncio
async def test_high_cpa_widgets_30days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 30d')
    assert log_resp(data, f'{COMMAND}_30days.txt')


@pytest.mark.asyncio
async def test_high_cpa_widgets_90days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD} 90d')
    assert log_resp(data, f'{COMMAND}_90days.txt')
