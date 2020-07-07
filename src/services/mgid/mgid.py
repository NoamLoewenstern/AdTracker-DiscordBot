import json
# import os
import logging
from typing import Any, Dict, List, Optional, Union

from errors import (InvalidCampaignId, InvalidEmailPassword,
                    InvalidPlatormCampaignName)
# from services.thrive import Thrive
from utils import (DictForcedStringKeys, alias_param, append_url_params,
                   filter_result_by_fields, update_url_params)

from ..common.platform import PlatformService
from ..common.utils import add_interval_startend_dates
# from ..thrive.schemas import CampaignExtendedInfoStats
from . import urls
from .parameter_enums import DateIntervalParams
from .schemas import (CampaignBaseData, CampaignData, CampaignGETResponse,
                      CampaignStat, CampaignStatDayDetailsGETResponse,
                      CampaignStatsBySiteGETResponse, MergedWithThriveStats,
                      StatsAllCampaignGETResponse, WidgetSourceStats,
                      WidgetStats)
from .utils import (add_token_to_uri, fix_date_interval_value,
                    update_client_id_in_uri)


def adjust_dateInterval_params(func):
    alias_param_dateInterval = alias_param(
        alias='dateInterval',
        key='time_interval',
        callback=lambda value: fix_date_interval_value(value.lower()) if value else value
    )
    add_startend_dates_by_dateInterval = add_interval_startend_dates('dateInterval')
    return alias_param_dateInterval(add_startend_dates_by_dateInterval(func))


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
            campaigns = self.list_campaigns(fields=['id', 'name', 'status', 'statistics'])
            self._campaigns = self._update_campaigns(campaigns)
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
                       **kwargs) -> list:
        url = urls.CAMPAIGNS.LIST
        if campaign_id is not None:
            url = urls.CAMPAIGNS.LIST + '/' + str(campaign_id)
        if limit and start is not None:
            url = update_url_params(url, {'limit': limit, 'start': start})
        if fields:
            url = append_url_params(url, {'fields':  json.dumps(fields, separators=(',', ':'))})
        resp = self.get(url).json()
        if campaign_id is not None:
            resp_model = CampaignData(**resp)
            campaigns = [resp_model]
        else:
            resp_model = CampaignGETResponse.parse_obj(resp)
            campaigns = resp_model.__root__.values()
            campaigns = [camp for camp in campaigns]
            self._update_campaigns(campaigns)
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

    @adjust_dateInterval_params
    def stats_campaign_pure_platform(self,
                                     campaign_id: str = None,
                                     dateInterval: DateIntervalParams = 'today',
                                     as_json=True,
                                     **kwargs) -> List[CampaignStat]:
        url = urls.CAMPAIGNS.STATS_DAILY
        url = update_url_params(url, {'dateInterval': dateInterval,
                                      'startDate': kwargs.get('startDate', ''),
                                      'endDate': kwargs.get('endDate', '')})
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

    def stats_campaign(self, *,
                       campaign_id: str = None,
                       fields: Optional[List[str]] = ['id', 'name', 'clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit'],  # CampaignStat
                       # revenue <- rev, profit'],  # MergedWithThriveStats
                       **kwargs) -> List['MergedWithThriveStats.dict']:
        kwargs.update({
            'campaign_id': campaign_id,
            'as_json': False,
        })
        stats = self.stats_campaign_pure_platform(**kwargs)
        tracker_result = self.thrive.stats_campaigns(
            campaign_id=self.get_thrive_id(self.campaigns[campaign_id]) if campaign_id else None,
            time_interval=kwargs.get('time_interval'),
        )
        merged_stats = self._merge_thrive_stats(stats, tracker_result, MergedWithThriveStats)
        result = filter_result_by_fields(merged_stats, fields)
        return result

    def spent_campaign(self, *,
                       campaign_id: str = None,
                       min_spent=0.0001,
                       fields: List[str] = ['name', 'id', 'spent'],
                       **kwargs) -> list:
        kwargs.update({
            'campaign_id': campaign_id,
            'fields': fields,
        })
        stats = self.stats_campaign_pure_platform(**kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

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

    def get_api_token(self, **kwargs) -> List:
        url = urls.Token.GET_CURRENT
        if not self.email or not self.password:
            raise InvalidEmailPassword(platform='MGID', data="Must Require Email And Password!")
        result = self.post(url, data={'email': self.email, 'password': self.password})
        return result

    @adjust_dateInterval_params
    def top_widgets(self, *,
                    campaign_id: str,
                    widget_id: str = None,
                    dateInterval: DateIntervalParams = 'today',
                    filter_limit: int = 5,
                    fields: List[str] = ['id', 'clicks', 'spent', 'buy', 'buyCost'],
                    **kwargs,
                    ) -> List[WidgetStats]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        url = urls.CAMPAIGNS.WIDGETS_STATS.format(campaign_id=campaign_id)
        if widget_id:
            url += f'/{widget_id}'
        url = update_url_params(url, {'dateInterval': dateInterval,
                                      'startDate': kwargs.get('startDate', ''),
                                      'endDate': kwargs.get('endDate', '')})
        resp = self.get(url).json()
        resp_model = CampaignStatsBySiteGETResponse.parse_obj(resp)

        widget_stats = []
        logging.info(f'campaign_id: {campaign_id}')
        for camp_widget_stats in resp_model.__root__.values():
            for stats in camp_widget_stats.values():
                for site_id, cur_widget_stats in stats.items():
                    widget_with_id = WidgetStats(id=site_id,
                                                 **cur_widget_stats.dict(exclude={'id'}))
                    widget_stats.append(widget_with_id)
        widget_stats.sort(key=lambda widget: widget.buy, reverse=True)
        filtered_widgets = widget_stats[:filter_limit]
        result = filter_result_by_fields(filtered_widgets, fields)
        return result

    @adjust_dateInterval_params
    def high_cpa_widgets(self, *,
                        campaign_id: str,
                        widget_id: str = None,
                        dateInterval: DateIntervalParams = 'today',
                        filter_limit: int = 5,
                        fields: List[str] = ['id', 'clicks', 'spent', 'buy', 'buyCost'],
                        **kwargs,
                        ) -> List[WidgetStats]:
        pass
