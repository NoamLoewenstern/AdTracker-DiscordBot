
import pytest

from main import handle_content

from . import PLATFORM, log_resp

TEST_CAMPAING_ID = 1023198
COMMAND = 'top-widgets'


@pytest.mark.asyncio
async def test_top_widgets():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID}')
    assert log_resp(data, f'{COMMAND}.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_top_widgets_3d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 3d')
    assert log_resp(data, f'{COMMAND}_3d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_top_widgets_7days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 7d')
    assert log_resp(data, f'{COMMAND}_7days.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_top_widgets_30days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 30d')
    assert log_resp(data, f'{COMMAND}_30days.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_top_widgets_90days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 90d')
    assert log_resp(data, f'{COMMAND}_90days.txt')
    assert len(data) != 0
