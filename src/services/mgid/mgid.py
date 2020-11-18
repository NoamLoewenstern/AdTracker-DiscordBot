import json
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from config import (DEFAULT_FILTER_NUMBER, MAX_URL_PARAMS_SIZE,
                    RUNNING_ON_SERVER)
from constants import DEBUG
from errors import APIError, ErrorList, InvalidEmailPasswordError
from errors.network import AuthError
from errors.platforms import (CampaignNameMissingTrackerIDError,
                              InvalidCampaignIDError)
# import os
from logger import logger
from pydantic.main import BaseModel

# from services.thrive import Thrive
from utils import (OPERATORS_MAP, alias_param, append_url_params, chunks,
                   format_float, update_url_params)

from ..common.common_service import TargetType, get_target_type_by_name
from ..common.platform import PlatformService
from ..common.schemas import BaseModel
from ..common.utils import (add_interval_startend_dates, fields_list_hook,
                            filter_result_by_fields)
# from ..thrive.schemas import CampaignExtendedInfoStats
from . import urls
from .parameter_enums import DateIntervalParams
from .schemas import (CampaignBaseData, CampaignData, CampaignGETResponse,
                      CampaignStat, CampaignStatDayDetailsGETResponse,
                      CampaignStatDayDetailsSummary,
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
    def __init__(self,
                 client_id: str,
                 token: str,
                 thrive: 'Thrive',
                 email: str = '',
                 password: str = '',
                 *args,
                 **kwargs):
        self.token = token
        super().__init__(thrive=thrive,
                         base_url=urls.CAMPAIGNS.BASE_URL,
                         url_hooks=[
                             lambda url: add_token_to_url(url, self.token),
                             lambda url: update_client_id_in_url(url, client_id)
                         ],
                         platform='MGID',
                         email=email,
                         password=password,
                         *args, **kwargs)

    def renew_token(self):
        if not self.email or not self.password:
            raise AuthError(
                platform='MGID',
                message='Need To Renew Token OR Enter email+password in ENV-VARIABLES For This Account.',
                explain='Token Error')
        url = urls.TOKEN.GET_CURRENT
        url = update_url_params(url, {'email': self.email, 'password': self.password})
        result = self.post(url).json()
        self.token = result['token']

    def _req(self, *args, **kwargs):
        try:
            return super()._req(*args, **kwargs)
        except APIError as e:
            if 'ERROR_AUTHENTICATION_SIGNING_IN_ERROR' in json.dumps(e.data):
                self.renew_token()
                return super()._req(*args, **kwargs)
            raise e

    @property
    def campaigns(self):
        if not self._campaigns:
            campaigns = self.list_campaigns(fields=['id', 'name', 'status',
                                                    'statistics', 'spent', 'target_type'])
            self._campaigns = self._update_campaigns(campaigns)
        return self._campaigns

    def _removed_disabled(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]) -> Tuple[list, list]:
        active_camps = []
        disabled_camps = []
        for camp in campaigns:
            if camp['id'] in self.campaigns:
                active_camps.append(camp)
            else:
                disabled_camps.append(camp)
        return active_camps, disabled_camps

    def _add_names_to_campaigns_values(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]):
        for camp in campaigns:
            camp['name'] = self.campaigns[camp['id']]['name']
        return campaigns

    @fields_list_hook(CampaignData)
    def list_campaigns(self,
                       limit: int = None,
                       start: int = None,
                       campaign_id: int = None,
                       fields: List[str] = ['name', 'id'],
                       case_sensitive=False,
                       **kwargs) -> List[CampaignData]:
        """ returns the ACTIVE campaigns """
        url = urls.CAMPAIGNS.LIST
        if campaign_id:
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
        result = filter_result_by_fields(campaigns, fields, case_sensitive=case_sensitive)
        return result

    @fields_list_hook(CampaignStatDayDetailsSummary)
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
    @fields_list_hook(CampaignStat)
    def stats_campaign_pure_platform(self,
                                     campaign_id: str = None,
                                     dateInterval: DateIntervalParams = 'today',
                                     startDate: str = '',
                                     endDate: str = '',
                                     as_json=True,
                                     **kwargs) -> List[CampaignStat]:
        url = urls.CAMPAIGNS.STATS_DAILY
        url = update_url_params(url, {'dateInterval': dateInterval,
                                      'startDate': startDate,
                                      'endDate': endDate})
        resp = self.get(url).json()
        resp_model = StatsAllCampaignGETResponse(**resp)
        all_stats = resp_model.campaigns_stat.values()
        stats, disabled_camps = self._removed_disabled(all_stats)
        result = stats = self._add_names_to_campaigns_values(stats)
        if campaign_id:  # returning specific campaign
            if campaign_id in [c['id'] for c in disabled_camps]:
                raise InvalidCampaignIDError(campaign_id, platform='MGID',
                                             message=f'Campaign {campaign_id} Is Disabled or Deleted.')
            result = [stat for stat in stats if str(stat['id']) == campaign_id]
        if as_json:
            result = [stat.dict() for stat in result]
        return result

    @fields_list_hook(MergedWithThriveStats)
    def stats_campaign(self, *,
                       campaign_id: str = None,
                       fields: Optional[List[str]] = MergedWithThriveStats.fields_list(),  # CampaignStat
                       #    fields: Optional[List[str]] = ['id', 'name', 'platform_clicks', 'cost', 'conv',
                       #                                   'cpa', 'roi', 'revenue', 'profit', 'target_type'],  # CampaignStat

                       # revenue <- rev, profit'],  # MergedWithThriveStats
                       #    fetch_stats_by_campaign=False,
                       raise_=not RUNNING_ON_SERVER,
                       **kwargs) -> Tuple[List[MergedWithThriveStats], ErrorList]:
        def thrive_stats_by_campaign(campaign_id: str) -> List['thrive.CampaignStats']:
            thrive_id = self.get_thrive_id(self.campaigns[campaign_id], raise_=raise_)
            tracker_results = self.thrive.stats_campaigns(campaign_id=thrive_id,
                                                          time_interval=kwargs.get('time_interval'))
            return tracker_results

        stats: List[CampaignStat] = self.stats_campaign_pure_platform(campaign_id=campaign_id, **kwargs)
        ret_error_stats = ErrorList()
        # query_campaigns = [campaign_id] if campaign_id else list(self.campaigns.keys())
        # if campaign_id or fetch_stats_by_campaign:  # all campaigns
        #     tracker_results = []
        #     for campaign_id in query_campaigns:
        #         try:
        #             cur_tracker_result = thrive_stats_by_campaign(campaign_id)
        #             if cur_tracker_result:
        #                 tracker_results.append(cur_tracker_result)
        #         except CampaignNameMissingTrackerIDError as e:
        #             ret_error_stats.append(e.dict())
        if campaign_id:
            try:
                tracker_results = thrive_stats_by_campaign(campaign_id)
            except CampaignNameMissingTrackerIDError as e:
                return [], ErrorList([e.dict()])
        else:
            tracker_results = self.thrive.stats_campaigns(time_interval=kwargs.get('time_interval'))

        merged_stats, error_stats = self._merge_thrive_stats(stats, tracker_results, MergedWithThriveStats)
        result = filter_result_by_fields(merged_stats, fields)
        return result, (ret_error_stats + error_stats)

    @fields_list_hook(CampaignStat)
    def spent_campaign(self, *,
                       campaign_id: str = None,
                       min_spent=0.0001,
                       fields: List[str] = ['name', 'id', 'spent'],
                       **kwargs) -> list:
        stats = self.stats_campaign_pure_platform(campaign_id=campaign_id, fields=fields, **kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    @fields_list_hook(CampaignStat, ['thrive_clicks', 'platform_clicks'])
    def campaign_bot_traffic(self, *,
                             campaign_id: str = None,
                             fields: List[str] = ['name', 'id', 'thrive_clicks', 'platform_clicks'],
                             **kwargs) -> Tuple[List, ErrorList]:
        stats, error_stats = self.stats_campaign(campaign_id=campaign_id,
                                                 #  fetch_stats_by_campaign=True,
                                                 fields=fields,
                                                 **kwargs)
        result = []
        for stat in stats:
            if not all(key in stat for key in ['name', 'id', 'thrive_clicks', 'platform_clicks']):
                continue
            bot_traffic = 0
            if stat['platform_clicks'] != 0:
                bot_traffic = 100 - (stat['thrive_clicks'] / stat['platform_clicks'] * 100)
            if bot_traffic != 100:
                bot_traffic = format_float(bot_traffic)
            result.append({
                'id': stat['id'],
                'name': stat['name'],
                'bot': f'{bot_traffic}%',
                'thrive_clicks': stat['thrive_clicks'],
                'platform_clicks': stat['platform_clicks'],
            })
        if not result:
            error_stats.append({'MSG': 'NO RESULT, Try Widening the Time-Interval'})
        return result, error_stats

    def get_api_token(self, **kwargs) -> List:
        url = urls.TOKEN.GET_CURRENT
        if not self.email or not self.password:
            raise InvalidEmailPasswordError(platform='MGID', data="Must Require Email And Password!")
        result = self.post(url, data={'email': self.email, 'password': self.password})
        return result

    @fields_list_hook(WidgetStats)
    @adjust_dateInterval_params
    def widgets_stats(self, *,
                      campaign_id: str,
                      widget_id: str = None,
                      dateInterval: DateIntervalParams = 'today',
                      startDate: str = '',
                      endDate: str = '',
                      filter_limit: int = '',
                      sort_key: str = 'conversions',
                      fields: List[str] = ['widget_id', 'spent', 'conversions', 'cpa'],
                      **kwargs,
                      ) -> List[WidgetStats]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        assert sort_key in WidgetStats.fields_list(), \
            f"'sort_key' must be of types: {WidgetStats.fields_list()}"

        url = urls.WIDGETS.LIST.format(campaign_id=campaign_id)
        if widget_id:
            url += f'/{widget_id}'
        url = update_url_params(url, {'dateInterval': dateInterval,
                                      'startDate': startDate,
                                      'endDate': endDate})
        resp = self.get(url).json()
        resp_model = CampaignStatsBySiteGETResponse.parse_obj(resp).__root__

        widget_stats: List[WidgetStats] = []
        for camp_widget_stats in resp_model.values():
            for stats in camp_widget_stats.values():
                for site_id, cur_widget_stats in stats.items():
                    widget_with_id = WidgetStats(widget_id=site_id,
                                                 id=campaign_id,
                                                 **cur_widget_stats.dict(exclude={'widget_id', 'id'}))
                    widget_stats.append(widget_with_id)

        widget_stats.sort(key=lambda widget: widget[sort_key], reverse=True)
        filtered_widgets = widget_stats[:int(filter_limit)] if filter_limit else widget_stats
        result = filter_result_by_fields(filtered_widgets, fields)

        # Checking if Given WidgetID Exists:
        if widget_id is not None and widget_id.lower() not in [str(e['widget_id']).lower() for e in result]:
            return [], ErrorList([f"No Such Widget Exists: '{widget_id}'"])

        return result

    @fields_list_hook(WidgetStats)
    def widgets_top(self, filter_limit: int = '', **kwargs) -> List[WidgetStats]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        if not filter_limit:
            filter_limit = DEFAULT_FILTER_NUMBER
        return self.widgets_stats(filter_limit=filter_limit, **kwargs)

    @fields_list_hook(WidgetStats)
    def widgets_filter_cpa(self, *,
                           threshold: float,
                           operator: Literal['eq', 'ne', 'lt', 'gt', 'le', 'ge'] = 'le',
                           fields: List[str] = ['widget_id', 'spent', 'conversions', 'cpa'],
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
                           if getattr(stat['cpa'], OPERATORS_MAP[operator])(float(threshold))]
        result = filter_result_by_fields(filtered_by_cpa, fields)
        return result

    @fields_list_hook(WidgetStats)
    def widgets_high_cpa(self, **kwargs) -> List[WidgetStats]:
        return self.widgets_filter_cpa(operator='ge', **kwargs)

    @fields_list_hook(WidgetStats)
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

    def _widgets_init_filter_to_blacklist(self, campaign_id: str) -> List:
        """ if is already blacklist ('except') - method does nothing
        return: current/new list of 'blacklisted' widgets
        """
        # CLEANING CURRENT FILTER ON WIDGETS IF IS NOT BLACKLIST
        camps_stats = self.list_campaigns(campaign_id=campaign_id,
                                          fields=['widgetsFilterUid'],
                                          case_sensitive=True)
        cur_filterType = camps_stats[0]['widgetsFilterUid']['filterType'].lower()
        # if is empty dict - will return empty list
        cur_filterType_widgets = camps_stats[0]['widgetsFilterUid']['widgets'] or []

        if cur_filterType == 'only':
            self.widgets_turn_on_all(campaign_id=campaign_id)
            return []
        if cur_filterType_widgets and isinstance(cur_filterType_widgets, dict):
            cur_filterType_widgets = list(cur_filterType_widgets.keys())
        return cur_filterType_widgets

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

    def _widgets_pause(self, campaign_id: str, list_widgets: List[str]) -> List[str]:
        # CLEANING CURRENT FILTER ON WIDGETS IF IS NOT BLACKLIST
        # if is already blacklist ('except') - method does nothing
        cur_blacklist = self._widgets_init_filter_to_blacklist(campaign_id=campaign_id)
        widgets_to_pause = [widget for widget in list_widgets if widget not in cur_blacklist]
        url = urls.WIDGETS.PAUSE.format(campaign_id=campaign_id)
        for chunk_widgets in chunks(widgets_to_pause, MAX_URL_PARAMS_SIZE):
            url = update_url_params(url, {'widgetsFilterUid': "include,except,{ids}"
                                          .format(ids=','.join(chunk_widgets))})
            resp = self.patch(url)
            self._validate_widget_filter_resp(resp)
        return widgets_to_pause

    @adjust_dateInterval_params
    def widgets_kill_longtail(self, *,
                              campaign_id: str,
                              threshold: int,
                              dateInterval: DateIntervalParams = 'today',
                              **kwargs) -> dict:
        widgets_stats = self.widgets_stats(campaign_id=campaign_id,
                                           sort_key='spent',
                                           fields=['id', 'widget_id', 'spent'],
                                           dateInterval=dateInterval,
                                           **kwargs)
        filtered_widgets: List[str] = [widget['widget_id'] for widget in widgets_stats
                                       if widget['spent'] < float(threshold)]

        widgets_paused_ids = self._widgets_pause(campaign_id=campaign_id, list_widgets=filtered_widgets)
        widgets_paused_stats = [
            widget for widget in widgets_stats if widget['widget_id'] in widgets_paused_ids]
        widgets_paused_total_spent = sum(widget['spent'] for widget in widgets_paused_stats)
        time_interval = kwargs.get('time_interval', None)
        return {
            'Success': True,
            'Action': f'Paused {len(widgets_paused_ids)} Widgets',
            # 'Number Widgets': len(widgets_to_pause),
            f"Stopped Widgets' Spent Amount in Last {time_interval}": format_float(widgets_paused_total_spent),
            'Data': f'Campaign: {campaign_id}',
        }

    @adjust_dateInterval_params
    def widget_kill_bot_traffic(self, *,
                                campaign_id: str,
                                threshold: float,
                                dateInterval: DateIntervalParams = 'today',
                                raise_=not RUNNING_ON_SERVER,
                                **kwargs) -> List[Dict]:
        try:
            thrive_id = self.get_thrive_id(self.campaigns[campaign_id], raise_=raise_)
        except CampaignNameMissingTrackerIDError as e:
            return [], ErrorList([e.dict()])
        tracker_widgets = self.thrive.stats_widgets(
            platform_name='mgid',
            campaign_id=thrive_id,
            time_interval=kwargs.get('time_interval', ''),
            sort_key='thrive_clicks',
            fields=['id', 'widget_id', 'thrive_clicks'])
        if not tracker_widgets:  # => No Clicks in Time-Range
            return {
                'Action': '0 Widgets Paused',
                'Data': '0 Clicks in *Tracker*, in Given Time-Interval',
            }
        self.thrive._remove_unknown_ids(tracker_widgets)
        tracker_widgets = self.thrive._convert_subids_to_uids(tracker_widgets)
        tracker_widgets_dict = {w['widget_id']: w for w in tracker_widgets}

        widgets = self.widgets_stats(campaign_id=campaign_id,
                                     sort_key='platform_clicks',
                                     fields=['id', 'widget_id', 'platform_clicks', 'spent'],
                                     **kwargs)
        widgets = [w for w in widgets if w['platform_clicks'] != 0]
        widgets_dict = {w['widget_id']: w for w in widgets}
        if not widgets:  # => No Clicks in Time-Range in Platform.
            return {
                'Success': False,
                'Action': '0 Widgets Paused',
                'Data': '0 Clicks in *Platform*, in Given Time-Interval',
            }

        """
        * the unique ids in the platform -> are all bot-traffic.
        * Because the tracker doesn't return widgets with 0 clicks,
        * then all the widgets which are in platform-widgets but not in tracker - they are bot traffic.
        TODO figure out what to do with those bot-traffic-widgets.
        """
        widgets_ids = set(widgets_dict)
        tracker_widgets_ids = set(tracker_widgets_dict)
        # common_ids = widgets_ids & tracker_widgets_ids

        just_in_platform = widgets_ids - tracker_widgets_ids
        just_in_platform_widgets = [w for w in widgets if w['widget_id'] in just_in_platform]
        just_in_platform_widgets_sum_spent = sum(widget['spent'] for widget in just_in_platform_widgets)

        just_in_tracker = tracker_widgets_ids - widgets_ids
        # logger.info('[MGID] [widget_kill_bot_traffic] Platform Widgets & Tracker Widgets Differences: '
        #             #   f'len(just_in_platform):{len(just_in_platform)}\nlen(just_in_tracker):{len(just_in_tracker)}')
        #             f'{just_in_platform=}\n{just_in_tracker=}')

        merged_widget_data = self._merge_and_update_list_objects(
            tracker_widgets_dict,
            widgets_dict,
            just_common=True)

        bot_widgets_ids = []
        for widget in merged_widget_data:
            # Assuming thrive_clicks is over 0 (if was 0 - it would not have returned from tracker.)
            bot_percent = 100 - (widget['thrive_clicks'] / widget['platform_clicks'] * 100)
            if bot_percent > int(threshold):
                bot_widgets_ids.append(widget['widget_id'])
        widgets_paused_ids = self._widgets_pause(campaign_id=campaign_id, list_widgets=bot_widgets_ids)
        widgets_paused_stats = [
            widget for widget in merged_widget_data if widget['widget_id'] in widgets_paused_ids]
        widgets_paused_sum_spent = sum(widget['spent'] for widget in widgets_paused_stats)
        time_interval = kwargs.get('time_interval', None)
        # logger.debug(f'[{campaign_id}] Paused Widgets: {len(bot_widgets_ids)} / {len(merged_widget_data)}')
        optional_data = {}
        if just_in_platform:
            optional_data.update({'Widgets Not In Tracker Number': len(just_in_platform),
                                  'Widgets Not In Tracker Spent Sum': format_float(just_in_platform_widgets_sum_spent),
                                  })

        return {
            # 'Success': True,
            'Action': f'Paused {len(widgets_paused_ids)} Widgets',
            # 'Number Widgets': len(widgets_to_pause),
            f"Stopped Widgets' Spent Amount in Last {time_interval}": format_float(widgets_paused_sum_spent),
            'Data': f'Campaign: {campaign_id}',
            **optional_data,
        }
