import pytest

from main import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp


@pytest.mark.asyncio
async def test_stats_day_details_all_campaigns():
    data = await handle_content(f'/{PLATFORM} stats')
    assert log_resp(data, 'stats_day_details_all_campaigns.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details():
    data = await handle_content(f'/{PLATFORM} stats {TEST_CAMPAING_ID}')
    assert log_resp(data, 'stats_day_details.txt')
    assert len(data) != 0
