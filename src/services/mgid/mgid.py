import json
# import os
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from config import MAX_URL_PARAMS_SIZE
from errors import (APIError, InvalidCampaignId, InvalidEmailPassword,
                    InvalidPlatormCampaignName)
# from services.thrive import Thrive
from utils import (DictForcedStringKeys, alias_param, append_url_params,
                   chunks, filter_result_by_fields, operator_factory,
                   update_url_params)

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
from .utils import (add_token_to_url, fix_date_interval_value,
                    update_client_id_in_url)


def adjust_dateInterval_params(func):
    alias_param_dateInterval = alias_param(
        alias='dateInterval',
        key='time_interval',
        callback=lambda value: fix_date_interval_value(value.lower()) if value else value
    )
    add_startend_dates_by_dateInterval = add_interval_startend_dates('dateInterval')
    return alias_param_dateInterval(add_startend_dates_by_dateInterval(func))


class MGid(PlatformService):
    def __init__(self, client_id: str, token: str, thrive, *args, **kwargs):
        super().__init__(thrive=thrive,
                         base_url=urls.CAMPAIGNS.BASE_URL,
                         url_hooks=[
                             lambda url: add_token_to_url(url, token),
                             lambda url: update_client_id_in_url(url, client_id)
                         ],
                         *args, **kwargs)

    @property
    def campaigns(self):
        if self._campaigns is None:
            campaigns = self.list_campaigns(fields=['id', 'name', 'status',
                                                    'statistics', 'spent', 'target_type'])
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
                       fields: Optional[List[str]] = ['id', 'name', 'platform_clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit', 'target_type'],  # CampaignStat
                       # revenue <- rev, profit'],  # MergedWithThriveStats
                       **kwargs) -> List['MergedWithThriveStats.dict']:
        stats = self.stats_campaign_pure_platform(campaign_id=campaign_id, as_json=False, **kwargs)
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
        stats = self.stats_campaign_pure_platform(campaign_id=campaign_id, fields=fields, **kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    def campaign_bot_traffic(self, *,
                             campaign_id: str = None,
                             fields: List[str] = ['name', 'id', 'thrive_clicks', 'platform_clicks'],
                             **kwargs) -> list:
        stats = self.stats_campaign(campaign_id=campaign_id, fields=fields, **kwargs)
        result = []
        for stat in stats:
            bot_traffic = 0
            if stat['platform_clicks'] != 0:
                bot_traffic = stat['thrive_clicks'] / stat['platform_clicks'] * 100
            if bot_traffic != 100:
                bot_traffic = f'{bot_traffic:02}'
            result.append({
                stat['name']: f'{bot_traffic}%',
                'thrive_clicks': stat['thrive_clicks'],
                'platform_clicks': stat['platform_clicks'],
            })
        return result

    def get_api_token(self, **kwargs) -> List:
        url = urls.TOKEN.GET_CURRENT
        if not self.email or not self.password:
            raise InvalidEmailPassword(platform='MGID', data="Must Require Email And Password!")
        result = self.post(url, data={'email': self.email, 'password': self.password})
        return result

    @adjust_dateInterval_params
    def widgets_stats(self, *,
                      campaign_id: str,
                      widget_id: str = None,
                      dateInterval: DateIntervalParams = 'today',
                      filter_limit: int = '',
                      sort_key: str = 'conversions',
                      fields: List[str] = ['id', 'spent', 'conversions', 'cpa'],
                      **kwargs,
                      ) -> List[WidgetStats]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        assert sort_key in WidgetStats.__fields__.keys(), \
            f"'sort_key' must be of types: {list(WidgetStats.__fields__.keys())}"

        url = urls.WIDGETS.LIST.format(campaign_id=campaign_id)
        if widget_id:
            url += f'/{widget_id}'
        url = update_url_params(url, {'dateInterval': dateInterval,
                                      'startDate': kwargs['startDate'] or '',
                                      'endDate': kwargs['endDate'] or ''})
        resp = self.get(url).json()
        resp_model = CampaignStatsBySiteGETResponse.parse_obj(resp)

        widget_stats: List[WidgetStats] = []
        for camp_widget_stats in resp_model.__root__.values():
            for stats in camp_widget_stats.values():
                for site_id, cur_widget_stats in stats.items():
                    widget_with_id = WidgetStats(id=site_id,
                                                 **cur_widget_stats.dict(exclude={'id'}))
                    widget_stats.append(widget_with_id)
        widget_stats.sort(key=lambda widget: widget[sort_key], reverse=True)
        filtered_widgets = widget_stats[:int(filter_limit)] if filter_limit else widget_stats
        result = filter_result_by_fields(filtered_widgets, fields)
        return result

    def widgets_top(self, filter_limit: int = 5, **kwargs) -> List[WidgetStats]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        return self.widgets_stats(filter_limit=filter_limit, **kwargs)

    def widgets_filter_cpa(self, *,
                           threshold: float,
                           operator: Union['eq', 'ne', 'lt', 'gt', 'le', 'ge'] = 'le',
                           fields: List[str] = ['id', 'spent', 'conversions', 'cpa'],
                           **kwargs,
                           ) -> List[WidgetStats]:
        """
        Get list of all the widgets (Where Conversions > 1) of a given {campaignNameOrId}
        which had CPA of less than {threshold}
        """
        widgets_stats = self.widgets_stats(sort_key='cpa', **kwargs)
        filtered_by_conversions = [stat for stat in widgets_stats if stat['conversions'] > 0]
        filtered_by_cpa = [stat for stat in filtered_by_conversions
                           # the operator is used here:
                           if getattr(stat['cpa'], operator_factory[operator])(float(threshold))]
        result = filter_result_by_fields(filtered_by_cpa, fields)
        return result

    def widgets_high_cpa(self, **kwargs) -> List[WidgetStats]:
        return self.widgets_filter_cpa(operator='ge', **kwargs)

    def widgets_low_cpa(self, **kwargs) -> List[WidgetStats]:
        return self.widgets_filter_cpa(operator='le', **kwargs)

    def _validate_widget_filter_resp(self, resp):
        if not resp.is_json or 'id' not in resp.json_content:
            raise APIError(platform='MGID',
                           data={**resp.json(),
                                    'url': resp.url,
                                    'reason': resp.reason,
                                    'errors': (resp.json().get('errors', '')
                                               if resp.is_json else resp.content),
                                    'status_code': resp.status_code},
                           explain=resp.reason)

    def _widgets_init_filter_to_blacklist(self, campaign_id: str) -> None:
        """ if is already blacklist ('except') - method does nothing """
        # CLEANING CURRENT FILTER ON WIDGETS IF IS NOT BLACKLIST
        camps_stats = self.list_campaigns(campaign_id=campaign_id, fields=['widgetsFilterUid'])
        cur_filterType = camps_stats[0]['widgetsFilterUid']['filterType'].lower()
        if cur_filterType == 'only':
            self.widgets_turn_on_all(campaign_id=campaign_id)

    def widgets_turn_on_all(self, campaign_id: str, **kwargs) -> dict:
        url_turn_off_filter = urls.WIDGETS.RESUME.format(campaign_id=campaign_id)
        url_turn_off_filter = update_url_params(url_turn_off_filter,
                                                {'widgetsFilterUid': 'include,off,1'})
        resp = self.patch(url_turn_off_filter)
        self._validate_widget_filter_resp(resp)
        return {
            'Success': True,
            'Action': 'Turned On All Widgets',
            'Data': f'Campaign: {campaign_id}',
        }

    def widgets_pause(self, campaign_id: str, list_widgets: List[str]) -> dict:
        # CLEANING CURRENT FILTER ON WIDGETS IF IS NOT BLACKLIST
        # if is already blacklist ('except') - method does nothing
        self._widgets_init_filter_to_blacklist(campaign_id=campaign_id)

        url = urls.WIDGETS.PAUSE.format(campaign_id=campaign_id)
        for chunk_widgets in chunks(list_widgets, MAX_URL_PARAMS_SIZE):
            url = update_url_params(url, {'widgetsFilterUid': "include,except,{ids}"
                                          .format(ids=','.join(chunk_widgets))})
            resp = self.patch(url)
            self._validate_widget_filter_resp(resp)

        return {
            'Success': True,
            'Action': f'Paused {len(list_widgets)} Widgets',
            'Data': f'Campaign: {campaign_id}',
        }

    @adjust_dateInterval_params
    def widgets_kill_longtail(self, *,
                              campaign_id: str,
                              threshold: int,
                              dateInterval: DateIntervalParams = 'today',
                              **kwargs) -> dict:
        widgets_stats = self.widgets_stats(campaign_id=campaign_id,
                                           sort_key='spent',
                                           fields=['id', 'spent'],
                                           **kwargs)
        filtered_widgets: List[str] = [widget['id'] for widget in widgets_stats
                                       if widget['spent'] < float(threshold)]

        result = self.widgets_pause(campaign_id=campaign_id, list_widgets=filtered_widgets)
        return result

    @adjust_dateInterval_params
    def widget_kill_bot_traffic(self, *,
                                campaign_id: str,
                                threshold: float,
                                dateInterval: DateIntervalParams = 'today',
                                **kwargs) -> List[Dict]:
        tracker_widgets = self.thrive._widgets_stats(
            platform_name='MGID',
            campaign_id=self.get_thrive_id(self.campaigns[campaign_id]),
            time_interval=kwargs.get('time_interval', ''),
            sort_key='thrive_clicks',
            fields=['id', 'thrive_clicks'])
        if not tracker_widgets:  # => No Clicks in Time-Range
            return {
                'Action': '0 Widgets Paused',
                'Data': '0 Clicks in Given Time-Interval',
            }
        self.thrive._remove_unknown_ids(tracker_widgets)
        tracker_widgets = self.thrive._convert_subids_to_uids(tracker_widgets)
        tracker_widgets_dict = {w['id']: w for w in tracker_widgets}

        widgets = self.widgets_stats(campaign_id=campaign_id,
                                     sort_key='platform_clicks',
                                     fields=['id', 'platform_clicks'],
                                     **kwargs)
        widgets = [w for w in widgets if w['platform_clicks'] != 0]
        widgets_dict = {w['id']: w for w in widgets}

        """
        * the unique ids in the platform -> are all bot-traffic.
        * Because the the tracker doesn't return widgets with 0 clicks,
        * then all the widgets which are in platform-widgets but not in tracker - they are bot traffic.
        TODO figure out what to do with those bot-traffic-widgets.
        """
        widgets_ids = set(widgets_dict)
        tracker_widgets_ids = set(tracker_widgets_dict)
        common_ids = widgets_ids & tracker_widgets_ids

        just_in_platform = widgets_ids - tracker_widgets_ids
        just_in_tracker = tracker_widgets_ids - widgets_ids
        logging.info('[MGID] [widget_kill_bot_traffic] Platform Widgets & Tracker Widgets Differences: '
                     #   f'len(just_in_platform):{len(just_in_platform)}\nlen(just_in_tracker):{len(just_in_tracker)}')
                     f'{just_in_platform=}\n{just_in_tracker=}')

        merged_widget_data = self._merge_and_update_list_objects(
            tracker_widgets_dict,
            widgets_dict,
            just_common=True)

        bot_widgets_ids = []
        for widget in merged_widget_data:
            # Assuming thrive_clicks is over 0 (if was 0 - it would not have returned from tracker.)
            bot_percent = widget['thrive_clicks'] / widget['platform_clicks'] * 100
            if bot_percent > int(threshold):
                bot_widgets_ids.append(widget['id'])
        result = self.widgets_pause(campaign_id=campaign_id, list_widgets=bot_widgets_ids)
        logging.debug(f'[{campaign_id}] Paused Widgets: {len(bot_widgets_ids)} / {len(merged_widget_data)}')
        return result
