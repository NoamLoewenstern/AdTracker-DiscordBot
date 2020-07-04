import pytest

from main import handle_content

from . import PLATFORM, TEST_CAMPAING_ID, log_resp


@pytest.mark.asyncio
async def test_spent():
    data = await handle_content(f'/{PLATFORM} spent {TEST_CAMPAING_ID} /fields:id,name,spent')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, 'spent.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns():
    data = await handle_content(f'/{PLATFORM} spent /fields:id,name,spent')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, 'spent_all_campaigns.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns_3d():
    data = await handle_content(f'/{PLATFORM} spent /fields:id,name,spent /time_range:3d')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, 'spent_all_campaigns_3d.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns_7d():
    data = await handle_content(f'/{PLATFORM} spent /fields:id,name,spent /time_range:7d')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, 'spent_all_campaigns_7d.txt')
    assert len(data) > 0


@pytest.mark.asyncio
async def test_spent_all_campaigns_30d():
    data = await handle_content(f'/{PLATFORM} spent /fields:id,name,spent /time_range:30d')
    data = data if data else 'no results for spent over 0'
    assert log_resp(data, 'spent_all_campaigns_30d.txt')
    assert len(data) > 0
