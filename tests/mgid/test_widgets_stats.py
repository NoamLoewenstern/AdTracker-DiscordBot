
import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content
from tests.zeropark.test_widgets_stats import WIDGET_ID

from . import PLATFORM, log_resp

TEST_CAMPAING_ID = 1023198
WIDGET_ID = 5662589
COMMAND = 'widgets-stats'


@pytest.mark.asyncio
async def test_test_widget_stats_non_existing():
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
