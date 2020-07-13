
import pytest

from main import handle_content

from . import PLATFORM, log_resp

TEST_CAMPAING_ID = 1071615
COMMAND = 'widgets-kill-longtail'
THRESHHOLD = '5'


@pytest.mark.asyncio
async def test_widgets_kill_longtail_5():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID} {THRESHHOLD}')
    assert log_resp(data, f'{COMMAND}.txt')
    assert len(data) != 0
