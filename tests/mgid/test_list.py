
import pytest

from main import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, TEST_DATE, log_resp


@pytest.mark.asyncio
async def test_list_campaigns():
    data = await handle_content(f'/{PLATFORM} list')
    assert log_resp(data, 'list_campaigns.txt')
    assert len(data) >= 0


@pytest.mark.asyncio
async def test_list_campaign_id():
    data = await handle_content(f'/{PLATFORM} list {TEST_CAMPAING_ID}')
    assert log_resp(data, 'list_campaigns_id.txt')
    assert len(data) >= 0
