
import pytest

from main import handle_content

from . import PLATFORM, log_resp

TEST_CAMPAING_ID = 'ba9b59f0-7b43-11ea-9558-0a06ea97c507'
COMMAND = 'widgets-turn-on-all'


@pytest.mark.asyncio
async def test_widgets_turn_on_all():
    data = await handle_content(f'/{PLATFORM} {COMMAND} {TEST_CAMPAING_ID}')
    assert log_resp(data, f'{COMMAND}.txt')
    assert len(data) != 0
