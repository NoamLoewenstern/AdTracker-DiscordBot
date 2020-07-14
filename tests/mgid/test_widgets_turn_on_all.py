
import pytest

from main import handle_content

from . import PLATFORM, log_resp

TEST_CAMPAING_ID = 1071615
COMMAND = 'widgets-turn-on-all'


async def widgets_turn_on_all(camp_id=TEST_CAMPAING_ID):
    return await handle_content(f'/{PLATFORM} {COMMAND} {camp_id}')


@pytest.mark.asyncio
async def test_widgets_turn_on_all(camp_id=TEST_CAMPAING_ID):
    data = await handle_content(f'/{PLATFORM} {COMMAND} {camp_id}')
    assert log_resp(data, f'{COMMAND}.txt')
    assert len(data) != 0
