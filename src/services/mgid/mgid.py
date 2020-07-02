import json
# import os
import logging
from typing import Any, Dict, List, Optional, Union

from errors import InvalidCampaignId, InvalidPlatormCampaignName
# from services.thrive import Thrive
from utils import (DictForcedStringKeys, alias_param, append_url_params,
                   filter_result_by_fields, update_url_params)

from ..common.platform import PlatformService
# from ..thrive.schemas import CampaignExtendedInfoStats
from . import urls
from .parameter_enums import DateIntervalParams
from .schemas import (CampaignBaseData, CampaignData, CampaignGETResponse,
                      CampaignStat, CampaignStatDayDetailsGETResponse,
                      MergedWithThriveStats, StatsAllCampaignGETResponse)
from .utils import (add_token_to_uri, fix_date_interval_value,
                    update_client_id_in_uri)

alias_param_dateInterval = alias_param(
    alias='dateInterval',
    key='time_interval',
    callback=lambda value: fix_date_interval_value(value.lower()) if value else value
)


class MGid(PlatformService):
    # TODO check different types of statuses - to filter out the deleted ones

    def __init__(self, client_id: str, token: str, thrive, *args, **kwargs):
        super().__init__(thrive=thrive,
                         base_url=urls.CAMPAIGNS.BASE_URL,
                         uri_hooks=[
                             lambda uri: add_token_to_uri(uri, token),
                             lambda uri: update_client_id_in_uri(uri, client_id)
                         ],
                         *args, **kwargs)

    @property
    def campaigns(self):
        if self._campaigns is None:
            campaigns = self.list_campaigns(fields=['id', 'name', 'status', 'statistics'],
                                            as_json=False)
            self._campaigns = DictForcedStringKeys({campaign['id']: campaign for campaign in campaigns})
        return self._campaigns

    def _removed_deleted(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]):
        return [camp for camp in campaigns if camp['id'] in self.campaigns]

    def _add_names_to_campaigns_values(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]):
        for camp in campaigns:
            camp['name'] = self.campaigns[camp['id']]['name']
        return campaigns

    def list_campaigns(self,
                       limit: int = None,
                       start: int = None,
                       campaign_id: int = None,
                       fields: List[str] = ['name', 'id'],
                       as_json=True,
                       **kwargs) -> list:
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS
        if campaign_id is not None:
            url = urls.CAMPAIGNS.LIST_CAMPAIGNS + '/' + str(campaign_id)
        if limit and start is not None:
            url = update_url_params(url, {'limit': limit, 'start': start})
        if fields:
            url = append_url_params(url, {'fields':  json.dumps(fields, separators=(',', ':'))})
        resp = self.get(url).json()
        if campaign_id is None:
            resp_model = CampaignGETResponse.parse_obj(resp)
            campaigns = resp_model.__root__.values()
        else:
            resp_model = CampaignData(**resp)
            campaigns = [resp_model]
        if as_json:
            campaigns = [camp.dict() for camp in campaigns]
        result = filter_result_by_fields(campaigns, fields)
        return result

    def stats_day_details(self,
                          campaign_id: int,
                          date: str,
                          type: str = 'byClicksDetailed',
                          fields: List[str] = None,  # CampaignStatDayDetailsSummary
                          **kwargs) -> dict:
        url = urls.CAMPAIGNS.STATS_DAILY_DETAILED.format(campaign_id=campaign_id)
        url = update_url_params(url, {'type': type, 'date': date})
        resp = self.get(url).json()
        resp_model = CampaignStatDayDetailsGETResponse(**resp)
        summary = resp_model.statistics.summary.dict()
        result = summary
        if fields:
            result = {field: summary[field] for field in fields}
        return result

    @alias_param_dateInterval
    def stats_campaign_pure_platform(self,
                                     campaign_id: str = None,
                                     dateInterval: DateIntervalParams = 'today',
                                     as_json=True,
                                     **kwargs) -> List[CampaignStat]:
        url = urls.CAMPAIGNS.STATS_DAILY
        url = update_url_params(url, {'dateInterval': dateInterval})
        resp = self.get(url).json()
        resp_model = StatsAllCampaignGETResponse(**resp)
        stats = resp_model.campaigns_stat.values()
        stats = self._removed_deleted(stats)
        result = stats = self._add_names_to_campaigns_values(stats)
        if campaign_id is not None:  # returning specific campaign
            result = [stat for stat in stats if str(stat['id']) == campaign_id]
        if as_json:
            result = [stat.dict() for stat in result]
        return result

    @alias_param_dateInterval
    def stats_campaign(self, *,
                       campaign_id: str = None,
                       dateInterval: DateIntervalParams = 'today',
                       fields: Optional[List[str]] = ['id', 'name', 'clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit'],  # CampaignStat
                       # revenue <- rev, profit'],  # MergedWithThriveStats
                       as_json=True,
                       **kwargs) -> List['MergedWithThriveStats.dict']:
        kwargs.update({
            'campaign_id': campaign_id,
            'dateInterval': dateInterval,
            'as_json': False,
        })
        stats = self.stats_campaign_pure_platform(**kwargs)
        tracker_result = self.thrive.stats_campaigns(
            campaign_id=self.get_thrive_id(self.campaigns[campaign_id]) if campaign_id else None,
            time_interval=kwargs.get('time_interval'),
        )
        merged_stats = self._merge_thrive_stats(stats, tracker_result, MergedWithThriveStats)
        if as_json:
            merged_stats = [stat.dict() for stat in merged_stats]
        result = filter_result_by_fields(merged_stats, fields)
        return result

    @alias_param_dateInterval
    def spent_campaign(self, *,
                       campaign_id: str = None,
                       min_spent=0.0001,
                       dateInterval: DateIntervalParams = 'today',
                       fields: List[str] = ['name', 'id', 'spent'],
                       **kwargs) -> list:
        kwargs.update({
            'campaign_id': campaign_id,
            'dateInterval': dateInterval,
            'fields': fields,
        })
        stats = self.stats_campaign_pure_platform(**kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    @alias_param_dateInterval
    def bot_traffic(self, *,
                    campaign_id: str = None,
                    fields: List[str] = ['name', 'id', 'thrive_clicks', 'platform_clicks'],
                    **kwargs) -> list:
        stats = self.stats_campaign(campaign_id=campaign_id, fields=fields, **kwargs)
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
