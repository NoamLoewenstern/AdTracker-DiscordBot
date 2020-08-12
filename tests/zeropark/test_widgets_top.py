
import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from config import DEFAULT_FILTER_NUMBER
from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp

COMMAND = 'widgets-top'
TEST_CAMPAING_ID = 'e556d672-d6f0-11ea-9f7c-12e5dcaa70ed'


@pytest.mark.asyncio
async def test_top_widgets_help():
    data = await handle_content(f'/{PLATFORM} {COMMAND} -h')
    assert log_resp(data, f'{COMMAND}_help.txt')
    assert data.startswith('usage')

@pytest.mark.asyncio
async def test_top_widgets_help_id():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} -h')
    assert log_resp(data, f'{COMMAND}_help_id.txt')
    assert data.startswith('usage')


@pytest.mark.asyncio
async def test_top_widgets_list_fields():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} --{FIELDS_OPTIONS_FLAG}')
    assert log_resp(data, f'{COMMAND}_list_fields.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_top_widgets():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID}')
    assert log_resp(data, f'{COMMAND}.txt')
    assert data.count('conversions') == DEFAULT_FILTER_NUMBER


@pytest.mark.asyncio
async def test_top_widgets_3d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 3d')
    assert log_resp(data, f'{COMMAND}_3d.txt')
    assert data.count('conversions') == DEFAULT_FILTER_NUMBER


@pytest.mark.asyncio
async def test_top_widgets_7days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 7d')
    assert log_resp(data, f'{COMMAND}_7days.txt')
    assert data.count('conversions') == DEFAULT_FILTER_NUMBER


@pytest.mark.asyncio
async def test_top_widgets_30days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 30d')
    assert log_resp(data, f'{COMMAND}_30days.txt')
    assert data.count('conversions') == DEFAULT_FILTER_NUMBER


@pytest.mark.asyncio
async def test_top_widgets_90days():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 90d')
    assert log_resp(data, f'{COMMAND}_90days.txt')
    assert data.count('conversions') == DEFAULT_FILTER_NUMBER
