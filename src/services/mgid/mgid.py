import json
# import os
import logging
from typing import Any, Dict, List, Optional, Union

from errors import InvalidCampaignId, InvalidPlatormCampaignName
# from services.thrive import Thrive
from utils import (alias_param, append_url_params, filter_result_by_fields,
                   update_url_params)

from ..common import CommonService
# from ..thrive.schemas import CampaignExtendedInfoStats
from . import urls
from .parameter_enums import DateIntervalParams
from .schemas import (CampaignBaseData, CampaignData, CampaignGETResponse,
                      CampaignStat, CampaignStatDayDetailsGETResponse,
                      MergedWithThriveStats, StatsAllCampaignGETResponse)
from .utils import (DictForcedStringKeys, add_token_to_uri,
                    fix_date_interval_value, get_thrive_id_from_camp,
                    update_client_id_in_uri)

alias_param_dateInterval = alias_param(
    alias='dateInterval',
    key='time_interval',
    callback=lambda value: fix_date_interval_value(value.lower()) if value else value
)


class MGid(CommonService):
    # TODO check different types of statuses - to filter out the deleted ones

    def __init__(self, client_id: str, token: str, thrive):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL,
                         uri_hooks=[
                             lambda uri: add_token_to_uri(uri, token),
                             lambda uri: update_client_id_in_uri(uri, client_id)
                         ])
        self.__campaigns: Dict[str, Any] = None
        self.thrive = thrive

    @property
    def campaigns(self):
        if self.__campaigns is None:
            filter_fields = ['id', 'name', 'status', 'statistics']
            url = urls.CAMPAIGNS.LIST_CAMPAIGNS
            url = append_url_params(url, {'fields': json.dumps(filter_fields, separators=(',', ':'))})
            resp = self.get(url).json()
            resp_model = CampaignGETResponse.parse_obj(resp)
            campaigns = resp_model.__root__.values()

            self.__campaigns = DictForcedStringKeys({campaign.id: campaign for campaign in campaigns})
        return self.__campaigns

    @campaigns.setter
    def campaigns(self, d: dict):
        self.__campaigns = DictForcedStringKeys(d)

    def _removed_deleted(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]):
        return [camp for camp in campaigns if camp['id'] in self.campaigns]

    def _add_names_to_campaigns_values(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]):
        for camp in campaigns:
            camp['name'] = self.campaigns[camp['id']].name
        return campaigns

    def list_campaigns(self,
                       limit: int = None,
                       start: int = None,
                       campaign_id: int = None,
                       fields: List[str] = ['name', 'id'],
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

    def _merge_thrive_stats(self,
                            stats: List['CampaignStat.dict'],
                            thrive_results: List['CampaignExtendedInfoStats.dict']
                            ) -> List['MergedWithThriveStats.dict']:
        merged = []
        for stat in stats:
            camp_thrive_id = get_thrive_id_from_camp(stat)
            for thrive_result in thrive_results:
                if str(camp_thrive_id) == str(thrive_result['id']):
                    logging.debug(f"->\tMGID stats: {stat}\n\tTHRIVE stats: {thrive_result}")
                    # stat.update({**thrive_result, 'id': stat['id']})
                    merged_dict = {**thrive_result, **stat.dict()}
                    merged.append(MergedWithThriveStats(**merged_dict))
                    logging.debug(f"\tMERGED stats: {stat}")
        return merged

    @alias_param_dateInterval
    def stats_campaign_pure_platform(self,
                                     campaign_id: str = None,
                                     dateInterval: DateIntervalParams = 'today',
                                     as_json=True,
                                     **kwargs):
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
            result = [stat.dict() for stat in stats]
        return result

    @alias_param_dateInterval
    def stats_campaign(self, *,
                       campaign_id: str = None,
                       dateInterval: DateIntervalParams = 'today',
                       fields: Optional[List[str]] = ['id', 'name', 'clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit'],  # CampaignStat
                       # revenue <- rev, profit'],  # MergedWithThriveStats
                       **kwargs) -> List['MergedWithThriveStats.dict']:
        stats = self.stats_campaign_pure_platform(campaign_id=campaign_id, as_json=False, **kwargs)
        tracker_result = self.thrive.stats_campaigns(
            campaign_id=self.campaigns[campaign_id].thrive_id if campaign_id else None,
            time_interval=kwargs.get('time_interval'),
        )
        merged_stats = self._merge_thrive_stats(stats, tracker_result)
        if fields is None:
            result = [stat.dict() for stat in merged_stats]
        else:
            result = filter_result_by_fields(merged_stats, fields)
        # if campaign_id is not None:  # returning specific campaign
        #     result = [camp for camp in result if str(camp['id']) == campaign_id]
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
        stats = self.stats_campaign(**kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    @alias_param_dateInterval
    def bot_traffic(self, *,
                    campaign_id: str = None,
                    fields: List[str] = ['name', 'id', 'thrive_clicks', 'platform_clicks'],
                    **kwargs) -> list:
        stats = self.stats_campaign(campaign_id=campaign_id, fields=fields, **kwargs)
        return [{stat['name']: stat['thrive_clicks'] /
                 stat['platform_clicks'] if stat['platform_clicks'] != 0 else 0}
                for stat in stats]
