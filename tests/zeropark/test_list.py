import pytest

from bot.patterns import FIELDS_OPTIONS_FLAG
from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp

COMMAND = 'list'


@pytest.mark.asyncio
async def test_list_campaigns_list_fields():
    data = await handle_content(f'/{PLATFORM} {COMMAND} --{FIELDS_OPTIONS_FLAG}')
    assert log_resp(data, f'{COMMAND}_list_fields.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_list_campaigns_all():
    data = await handle_content(f'/{PLATFORM} {COMMAND}')
    assert log_resp(data, f'{COMMAND}_campaigns_all.txt')
    assert len(data) >= 0


@pytest.mark.asyncio
async def test_list_campaign_id():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID}')
    assert log_resp(data, f'{COMMAND}_campaigns_id.txt')
    assert len(data) >= 0
