from typing import List, Optional, Union

# from extensions import Thrive
from utils import (alias_param, append_url_params, filter_result_by_fields,
                   update_url_params)

from ..common import CommonService
from . import urls
from .schemas import CampaignStatsResponse, ExtendedStats, ListExtendedStats
from .utils import fix_date_interval_value

alias_param_interval = alias_param(
    alias='interval',
    key='time_interval',
    callback=lambda value: fix_date_interval_value(value.lower()) if value else value
)

alias_param_campaignNameOrId = alias_param(
    alias='campaignNameOrId',
    key='campaign_id',
    callback=lambda value: str(value)
)


class ZeroPark(CommonService):
    # TODO check different types of statuses - to filter out the deleted ones
    def __init__(self, token: str, thrive):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL)
        self.session.headers.update({'api-token': token})
        self.thrive = thrive

    @alias_param_interval
    @alias_param_campaignNameOrId
    def list_campaigns(self,
                       fields: Optional[List[str]] = ['id', 'name'],
                       **kwargs) -> list:
        result = self.stats_campaign_pure_platform(**kwargs)
        return filter_result_by_fields(result, fields)

    @alias_param_interval
    @alias_param_campaignNameOrId
    def stats_campaign_pure_platform(self,
                                     campaignNameOrId: str = None,
                                     interval: str = "TODAY",
                                     as_json=True,
                                     **kwargs) -> list:
        url = urls.CAMPAIGNS.STATS
        url = update_url_params(url, {'interval': interval})
        if campaignNameOrId is not None:
            url = update_url_params(url, {'campaignNameOrId': campaignNameOrId})
        resp = self.get(url).json()
        resp_model = CampaignStatsResponse(**resp)
        result = extended_stats = ListExtendedStats.parse_obj(
            [ExtendedStats(**elem.details.dict(), **elem.stats.dict())
             for elem in resp_model.elements]).__root__
        if campaignNameOrId is not None:  # returning specific campaign
            result = [stat for stat in extended_stats
                      if campaignNameOrId in (stat['id'], stat['name'])]

        # result = filter_result_by_fields(result, fields)
        if as_json:
            result = [stat.dict() for stat in result]
        return result

    @alias_param_interval
    @alias_param_campaignNameOrId
    def spent_campaign(self, *,
                       campaignNameOrId: str = None,
                       min_spent=0.0001,
                       interval: str = "TODAY",
                       fields: List[str] = ['name', 'id', 'spent'],
                       **kwargs) -> list:
        kwargs.update({
            'campaignNameOrId': campaignNameOrId,
            'interval': interval,
            'fields': fields,
        })
        stats = self.stats_campaign(**kwargs)
        stats = self.stats_campaign(**kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    @alias_param_interval
    @alias_param_campaignNameOrId
    def stats_campaign(self,
                       campaignNameOrId: str = None,
                       interval: str = "TODAY",
                       fields: Optional[List[str]] = ['id', 'name', 'clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit'],

                       **kwargs) -> list:
        kwargs.update({
            'campaignNameOrId': campaignNameOrId,
            'interval': interval,
            'fields': fields,
        })
        stats = self.stats_campaign_pure_platform(as_json=False, **kwargs)
        # TODO - COMBINE WITH THRIVE DATA
        # * spent -> from platfrom, cost -> from thrive
        result = filter_result_by_fields(stats, fields)
        return result
