
import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content

from . import PLATFORM, log_resp

TEST_CAMPAING_ID = 'e556d672-d6f0-11ea-9f7c-12e5dcaa70ed'
COMMAND = 'widgets-stats'
WIDGET_ID = 'xray-pix-xeowVSpG'


@pytest.mark.asyncio
async def test_widgets_stats_help():
    data = await handle_content(f'/{PLATFORM} {COMMAND} -h')
    assert log_resp(data, f'{COMMAND}_help.txt')
    assert data.startswith('usage')


@pytest.mark.asyncio
async def test_widgets_stats_help_id():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} -h')
    assert log_resp(data, f'{COMMAND}_help_id.txt')
    assert data.startswith('usage')


@pytest.mark.asyncio
async def test_widgets_stats_non_existing():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} 2d')
    log_resp(data, f'{COMMAND}_non_existing.txt')
    assert 'No Such Widget Exists' in data


@pytest.mark.asyncio
async def test_widgets_stats_list_fields():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} --{FIELDS_OPTIONS_FLAG}')
    assert log_resp(data, f'{COMMAND}_list_fields.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_widgets_stats_all():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID}')
    assert log_resp(data, f'{COMMAND}_all.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_widgets_stats_all_7d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} /time:7d')
    assert log_resp(data, f'{COMMAND}_all_7d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_widgets_stats_id():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {WIDGET_ID}')
    assert log_resp(data, f'{COMMAND}_id.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_widgets_stats_id_7d():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {WIDGET_ID} /time:7d')
    assert log_resp(data, f'{COMMAND}_id_7d.txt')
    assert len(data) != 0
