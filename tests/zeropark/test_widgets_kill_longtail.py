
import pytest

from tests import handle_content

from . import PLATFORM, log_resp
from .test_widgets_turn_on_all import widgets_turn_on_all

TEST_CAMPAING_ID = 'ba9b59f0-7b43-11ea-9558-0a06ea97c507'
COMMAND = 'widgets-kill-longtail'
THRESHHOLD = '5'


@pytest.mark.asyncio
async def test_widgets_kill_longtail_5():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD}')
    assert log_resp(data, f'{COMMAND}.txt')
    assert len(data) != 0
    await widgets_turn_on_all(TEST_CAMPAING_ID)
