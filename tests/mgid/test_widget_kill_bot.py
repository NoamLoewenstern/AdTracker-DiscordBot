
import pytest

from tests import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp
from .test_widgets_turn_on_all import widgets_turn_on_all

COMMAND = 'widgets-kill-bot'


@pytest.mark.asyncio
async def test_widgets_kill_bot_15d():
    THRESHOLD = 60
    RANGE = '15d'
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHOLD} {RANGE}')
    assert log_resp(data, f'{COMMAND}_{THRESHOLD}_{RANGE}.txt')
    await widgets_turn_on_all(TEST_CAMPAING_ID)
    # assert len(data) != 0


@pytest.mark.asyncio
async def test_widgets_kill_bot_30d():
    THRESHOLD = 60
    RANGE = '30d'
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHOLD} {RANGE}')
    assert log_resp(data, f'{COMMAND}_{THRESHOLD}_{RANGE}.txt')
    await widgets_turn_on_all(TEST_CAMPAING_ID)
    # assert len(data) != 0


@pytest.mark.asyncio
async def test_widgets_kill_bot_60d():
    THRESHOLD = 75
    RANGE = '60d'
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHOLD} {RANGE}')
    assert log_resp(data, f'{COMMAND}_{THRESHOLD}_{RANGE}.txt')
    await widgets_turn_on_all(TEST_CAMPAING_ID)
    # assert len(data) != 0
