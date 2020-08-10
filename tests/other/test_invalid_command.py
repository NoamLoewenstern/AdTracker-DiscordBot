
import pytest

from tests import handle_content

PLATFORM = 'mgid'
INVALID_COMMAND = "TEST-COMMAND"


@pytest.mark.asyncio
async def test_invalid_command():
    data = await handle_content(f'/{PLATFORM} {INVALID_COMMAND}')
    assert 'Invalid Command' in data or 'invalid choice' in data
