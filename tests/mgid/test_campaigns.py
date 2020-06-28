import os
from json import dumps
from pathlib import Path

import pytest

from extensions import mgid
from main import handle_content

# import logging

TEST_CAMPAING_ID = 1056026
TEST_DATE = '2020-05-28'
PLATFORM = 'mgid'


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    dbg_path.write_text(data)


@pytest.mark.asyncio
async def test_list_campaigns():
    limit_field = 5
    # data = mgid.list_campaigns({'limit': limit_field})
    data = await handle_content(f'/{PLATFORM} list')
    log_resp(data, 'list_campaigns_RESP.json')
    assert len(data) >= limit_field


@pytest.mark.asyncio
async def test_stats_day_details():
    # data = mgid.stats_day_details(
    #     campaign_id=TEST_CAMPAING_ID,
    #     date=TEST_DATE,
    #     type='byClicksDetailed',
    # )
    data = await handle_content(f'/{PLATFORM} stats {TEST_CAMPAING_ID}')
    log_resp(data, 'stats_day_details_RESP.json')
    assert len(data) != 0


# @pytest.mark.asyncio
# async def test_stats_all_campaigns():
#     data = mgid.stats_all_campaigns(
#         dateInterval='today',
#         fields=None,  # can filter return fields
#     )
#     log_resp(data, 'stats_all_campaigns_RESP.json')
#     assert len(data) != 0


@pytest.mark.asyncio
async def test_spent():
    data = await handle_content(f'/{PLATFORM} spent {TEST_CAMPAING_ID} /fields:id,name,spent')
    log_resp(data, 'spent_RESP.json')
    assert len(data) != 0


if __name__ == "__main__":
    test_list_campaigns()
