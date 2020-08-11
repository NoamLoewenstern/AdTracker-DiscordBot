
import pytest

from tests import handle_content

from . import PLATFORM, log_resp

TEST_CAMPAING_ID = 'e556d672-d6f0-11ea-9f7c-12e5dcaa70ed'
COMMAND = 'widgets-turn-on-all'


async def widgets_turn_on_all(camp_id=TEST_CAMPAING_ID):
    return await handle_content(f'/{PLATFORM} {COMMAND} {camp_id}')


@pytest.mark.asyncio
async def test_widgets_turn_on_all(camp_id=TEST_CAMPAING_ID):
    data = await handle_content(f'/{PLATFORM} {COMMAND} {camp_id}')
    assert log_resp(data, f'{COMMAND}.txt')
    assert len(data) != 0
