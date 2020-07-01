import os
from json import dumps
from pathlib import Path

import pytest

from extensions import mgid
from main import handle_content

# import logging

TEST_CAMPAING_ID = 1073503
TEST_CAMPAING_ID = 1071615
TEST_DATE = '2020-05-28'
PLATFORM = 'mgid'


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    if 'Internal Error' in data:
        return False
    dbg_path.write_text(data)
    return True


@pytest.mark.asyncio
async def test_list_campaigns():
    limit_field = 5
    # data = mgid.list_campaigns({'limit': limit_field})
    data = await handle_content(f'/{PLATFORM} list')
    assert log_resp(data, 'list_campaigns.txt')
    assert len(data) >= limit_field


@pytest.mark.asyncio
async def test_list_campaign_id():
    # limit_field = 5
    # data = mgid.list_campaigns({'limit': limit_field})
    data = await handle_content(f'/{PLATFORM} list {TEST_CAMPAING_ID}')
    assert log_resp(data, 'list_campaigns_id.txt')
    assert len(data) >= 0


@pytest.mark.asyncio
async def test_stats_day_details_all_campaigns():
    # data = mgid.stats_day_details(
    #     campaign_id=TEST_CAMPAING_ID,
    #     date=TEST_DATE,
    #     type='byClicksDetailed',
    # )
    data = await handle_content(f'/{PLATFORM} stats')
    assert log_resp(data, 'stats_day_details_all_campaigns.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details():
    # data = mgid.stats_day_details(
    #     campaign_id=TEST_CAMPAING_ID,
    #     date=TEST_DATE,
    #     type='byClicksDetailed',
    # )
    TEST_CAMPAING_ID = 1071615
    data = await handle_content(f'/{PLATFORM} stats {TEST_CAMPAING_ID}')
    assert log_resp(data, 'stats_day_details.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_stats_day_details_30days():
    # data = mgid.stats_day_details(
    #     campaign_id=TEST_CAMPAING_ID,
    #     date=TEST_DATE,
    #     type='byClicksDetailed',
    # )
    data = await handle_content(f'/{PLATFORM} stats {TEST_CAMPAING_ID} 30d')
    assert log_resp(data, 'stats_day_details_30days.txt')
    assert len(data) != 0


# @pytest.mark.asyncio
# async def test_stats_all_campaigns():
#     data = mgid.stats_all_campaigns(
#         dateInterval='today',
#         fields=None,  # can filter return fields
#     )
#     assert log_resp(data, 'stats_all_campaigns.txt')
#     assert len(data) != 0


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


@pytest.mark.asyncio
async def test_bot_traffic_1d():
    data = await handle_content(f'/{PLATFORM} bot-traffic {TEST_CAMPAING_ID} 1d')
    assert log_resp(data, 'bot_traffic_1d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_7d():
    data = await handle_content(f'/{PLATFORM} bot-traffic {TEST_CAMPAING_ID} 7d')
    assert log_resp(data, 'bot_traffic_7d.txt')
    assert len(data) != 0


@pytest.mark.asyncio
async def test_bot_traffic_all_campaigns_7d():
    data = await handle_content(f'/{PLATFORM} bot-traffic 7d')
    assert log_resp(data, 'bot_traffic_all_campaigns_7d.txt')
    assert len(data) != 0
