import logging
from typing import Any, Dict, List, Optional, Union

# from extensions import Thrive
from utils import (DictForcedStringKeys, alias_param, append_url_params,
                   filter_result_by_fields, update_url_params)

from ..common.platform import PlatformService
from . import urls
from .schemas import (CampaignStatsResponse, ExtendedStats, ListExtendedStats,
                      MergedWithThriveStats)
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


class ZeroPark(PlatformService):
    # TODO check different types of statuses - to filter out the deleted ones
    def __init__(self, token: str, thrive, *args, **kwargs):
        super().__init__(thrive=thrive,
                         base_url=urls.CAMPAIGNS.BASE_URL,
                         *args, **kwargs)
        self.session.headers.update({'api-token': token})

    @property
    def campaigns(self):
        if self._campaigns is None:
            campaigns = self.list_campaigns(fields=['id', 'name', 'status', 'statistics'],
                                            as_json=False)
            self._campaigns = DictForcedStringKeys({campaign.id: campaign for campaign in campaigns})
        return self._campaigns

    @alias_param_interval
    @alias_param_campaignNameOrId
    def list_campaigns(self,
                       fields: Optional[List[str]] = ['id', 'name'],
                       **kwargs) -> list:
        result = self.stats_campaign_pure_platform(**kwargs)
        result = filter_result_by_fields(result, fields)
        return result

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

        if as_json:
            result = [stat.dict() for stat in result]
        return result

    @alias_param_interval
    @alias_param_campaignNameOrId
    def stats_campaign(self,
                       campaignNameOrId: str = None,
                       interval: str = "TODAY",
                       fields: Optional[List[str]] = ['id', 'name', 'clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit'],
                       as_json=True,
                       **kwargs) -> List['MergedWithThriveStats.dict']:
        kwargs.update({
            'campaignNameOrId': campaignNameOrId,
            'interval': interval,
            'as_json': False,
        })
        stats = self.stats_campaign_pure_platform(**kwargs)
        # * spent -> from platfrom, cost -> from thrive
        tracker_result = self.thrive.stats_campaigns(
            campaign_id=self.get_thrive_id(self.campaigns[campaignNameOrId])
            if campaignNameOrId else None,
            time_interval=kwargs.get('time_interval'),
        )
        merged_stats = self._merge_thrive_stats(stats, tracker_result, MergedWithThriveStats)
        if as_json:
            merged_stats = [stat.dict() for stat in merged_stats]
        result = filter_result_by_fields(merged_stats, fields)
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
        stats = self.stats_campaign_pure_platform(**kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    @alias_param_interval
    @alias_param_campaignNameOrId
    def bot_traffic(self, *,
                    campaignNameOrId: str = None,
                    fields: List[str] = ['name', 'id', 'thrive_clicks', 'platform_clicks'],
                    **kwargs) -> list:
        stats = self.stats_campaign(campaignNameOrId=campaignNameOrId, fields=fields, **kwargs)
        result = []
        for stat in stats:
            bot_traffic = 0
            if stat['platform_clicks'] != 0:
                bot_traffic = stat['thrive_clicks'] / stat['platform_clicks']
            if bot_traffic != 100:
                bot_traffic = f'{bot_traffic:02}'
            result.append({
                stat['name']: f'{bot_traffic}%',
                'thrive_clicks': stat['thrive_clicks'],
                'platform_clicks': stat['platform_clicks'],
            })
        return result
