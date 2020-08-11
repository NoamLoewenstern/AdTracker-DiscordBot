
import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content

from . import PLATFORM, log_resp
from .test_widgets_turn_on_all import widgets_turn_on_all

# TEST_CAMPAING_ID = 'e556d672-d6f0-11ea-9f7c-12e5dcaa70ed'
TEST_CAMPAING_ID = 'e556d672-d6f0-11ea-9f7c-12e5dcaa70ed'
COMMAND = 'widgets-stats'
WIDGET_ID = 'xray-pix-xeowVSpG'


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
async def test_widgets_stats_id():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {WIDGET_ID}')
    assert log_resp(data, f'{COMMAND}_id.txt')
    assert len(data) != 0
