import math
from os import stat
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from config import (DEFAULT_FILTER_NUMBER, DEFAULT_TIME_INTERVAL,
                    MAX_BODY_SIZE, MAX_URL_PARAMS_SIZE, RUNNING_ON_SERVER)
from constants import DEBUG
from errors import APIError, ErrorList
from errors.platforms import CampaignNameMissingTrackerIDError
from logger import logger

# from extensions import Thrive
from utils import (OPERATORS_MAP, alias_param, append_url_params, chunks,
                   format_float, update_url_params)

from ..common.platform import PlatformService
from ..common.utils import (add_interval_startend_dates, fields_list_hook,
                            filter_result_by_fields)
from . import urls
from .schemas import (CampaignStatsResponse, ExtendedStats, ListExtendedStats,
                      MergedWithThriveStats, TargetStatsByCampaignResponse,
                      TargetStatsMergedData)
from .utils import fix_date_interval_value


def adjust_interval_params(func):
    alias_param_interval = alias_param(
        alias='interval',
        key='time_interval',
        callback=lambda value: fix_date_interval_value(value.lower()) if value else value
    )
    add_startend_dates_by_interval = add_interval_startend_dates(
        'interval',
        custom_date_key='CUSTOM',
        strftime=r'%d/%m/%Y')
    return alias_param_interval(add_startend_dates_by_interval(func))


alias_param_campaignNameOrId = alias_param(
    alias='campaignNameOrId',
    key='campaign_id',
    callback=lambda value: str(value) if value else value
)

alias_param_widget_name = alias_param(
    alias='widget_name',
    key='widget_id',
    callback=lambda value: str(value) if value else value
)


class ZeroPark(PlatformService):
    # TODO check different types of statuses - to filter out the deleted ones
    def __init__(self, token: str, thrive, *args, **kwargs):
        super().__init__(thrive=thrive,
                         base_url=urls.CAMPAIGNS.BASE_URL,
                         platform='ZeroPark',
                         *args, **kwargs)
        self.session.headers.update({'api-token': token})

    @property
    def campaigns(self):
        if self._campaigns is None:
            campaigns = self.list_campaigns(fields=['id', 'name', 'clicks',
                                                    'spent', 'bid', 'target_type'])
            self._campaigns = self._update_campaigns(campaigns)
        return self._campaigns

    @fields_list_hook(ExtendedStats)
    def list_campaigns(self,
                       fields: Optional[List[str]] = ['id', 'name'],
                       case_sensitive=False,
                       **kwargs) -> list:
        stats = self.stats_campaign_pure_platform(**kwargs)
        stats = filter_result_by_fields(stats, fields, case_sensitive=case_sensitive)
        return stats

    @fields_list_hook(ExtendedStats)
    @alias_param_campaignNameOrId
    @adjust_interval_params
    def stats_campaign_pure_platform(self,
                                     campaignNameOrId: str = None,
                                     interval: str = "TODAY",
                                     as_json=True,
                                     **kwargs) -> List[ExtendedStats]:
        url = urls.CAMPAIGNS.STATS
        url = update_url_params(url, {'interval': interval,
                                      'startDate': kwargs.get('startDate', ''),
                                      'endDate': kwargs.get('endDate', '')})
        if campaignNameOrId is not None:
            url = update_url_params(url, {'campaignNameOrId': campaignNameOrId})
        resp = self.get(url).json()
        resp_model = CampaignStatsResponse(**resp)
        result = extended_stats = ListExtendedStats.parse_obj([ExtendedStats(**elem.stats.dict(), **elem.details.dict())
                                                               for elem in resp_model.elements]).__root__
        if campaignNameOrId is not None:  # returning specific campaign
            result = [stat for stat in extended_stats
                      if campaignNameOrId in (stat['id'], stat['name'])]
        else:
            self._update_campaigns(result)
        if as_json:
            result = [stat.dict() for stat in result]
        return result

    @fields_list_hook(MergedWithThriveStats)
    @alias_param_campaignNameOrId
    def stats_campaign(self,
                       campaignNameOrId: str = None,
                       fields: Optional[List[str]] = ['id', 'name', 'platform_clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit', 'redirects', 'target_type'],
                       raise_=not RUNNING_ON_SERVER,
                       **kwargs) -> Tuple[List[ExtendedStats], ErrorList]:
        kwargs.update({
            'campaignNameOrId': campaignNameOrId,
            'as_json': False,
        })
        stats = self.stats_campaign_pure_platform(**kwargs)
        # * spent -> from platfrom, cost -> from thrive
        if campaignNameOrId:
            try:
                thrive_id = self.get_thrive_id(self.campaigns[campaignNameOrId], raise_=raise_)
            except CampaignNameMissingTrackerIDError as e:
                return [], ErrorList([e.dict()])
        else:
            thrive_id = None
        tracker_result = self.thrive.stats_campaigns(campaign_id=thrive_id,
                                                     time_interval=kwargs.get('time_interval'))
        merged_stats, error_stats = self._merge_thrive_stats(stats, tracker_result, MergedWithThriveStats)
        result = filter_result_by_fields(merged_stats, fields)
        return result, error_stats

    @fields_list_hook(ExtendedStats)
    def spent_campaign(self, *,
                       min_spent=0.0001,
                       fields: List[str] = ['name', 'id', 'spent'],
                       **kwargs) -> List[ExtendedStats]:
        kwargs.update({'fields': fields})
        stats = self.stats_campaign_pure_platform(**kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    def campaign_bot_traffic(self, *,
                             fields: List[str] = ['name', 'id', 'thrive_clicks', 'platform_clicks'],
                             **kwargs) -> list:
        stats, error_stats = self.stats_campaign(fields=fields, **kwargs)
        result = []
        for stat in stats:
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
        return result, error_stats

    def campaign_bot_traffic_by_widgets(self, *,
                                        fields: List[str] = ['name', 'id',
                                                             'thrive_clicks', 'platform_clicks'],
                                        **kwargs) -> list:
        stats, error_stats = self.stats_campaign(fields=fields, **kwargs)
        result = []
        for stat in stats:
            bot_traffic = 0
            if stat['platform_clicks'] != 0:
                bot_traffic = stat['thrive_clicks'] / stat['platform_clicks']
            if bot_traffic != 100:
                bot_traffic = format_float(bot_traffic)
            result.append({
                'id': stat['id'],
                'name': stat['name'],
                'bot': f'{bot_traffic}%',
                'thrive_clicks': stat['thrive_clicks'],
                'platform_clicks': stat['platform_clicks'],
            })
        return result, error_stats

    @adjust_interval_params
    def _widget_exists(self, *,
                       campaignNameOrId: str,
                       widget_name: str,
                       interval: str,
                       startDate: str,
                       endDate: str,
                       **kwargs) -> bool:
        url = urls.WIDGETS.LIST.format(campaign_id=campaignNameOrId)
        url = update_url_params(url, {'campaignId': campaignNameOrId,
                                      'interval': interval,
                                      'startDate': startDate,
                                      'endDate': endDate,
                                      'targetAddresses': widget_name,
                                      })

        resp = self.get(url).json()
        resp_model = TargetStatsByCampaignResponse.parse_obj(resp)
        if not resp_model.elements:
            return False
        return True

    @fields_list_hook(TargetStatsMergedData)
    @alias_param_campaignNameOrId
    @alias_param_widget_name
    @adjust_interval_params
    def widgets_stats(self, *,
                      campaignNameOrId: str,
                      interval: str = 'TODAY',
                      widget_name: str = None,
                      filter_limit: int = None,
                      sort_key: str = 'CONVERSIONS',
                      state: Union[Literal['ACTIVE', 'PAUSED']] = None,
                      fields: List[str] = ['target', 'spent', 'conversions', 'ecpa'],
                      **kwargs) -> List[TargetStatsMergedData]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        assert not filter_limit or str(filter_limit).isnumeric(), "'filter_limit' Must Be Number."
        assert sort_key in (allowed := ['SPENT', 'NAME', 'GEO', 'TYPE', 'BUDGET', 'STATE',
                                        'REDIRECTS', 'CONVERSIONS', 'PAYOUT']), f"'sort_key' allowed values: {allowed}"

        def calc_num_pages(url):
            check_limit = 2  # just to get total
            url = update_url_params(url, {'limit': check_limit})
            resp = self.get(url).json()
            resp_model: TargetStatsByCampaignResponse = TargetStatsByCampaignResponse.parse_obj(resp)
            pages = resp_model.total / MAX_BODY_SIZE
            return math.ceil(pages)
        url = urls.WIDGETS.LIST.format(campaign_id=campaignNameOrId)
        url = update_url_params(url, {'campaignId': campaignNameOrId,
                                      'interval': interval,
                                      'startDate': kwargs.get('startDate', ''),
                                      'endDate': kwargs.get('endDate', ''),
                                      'sortColumn': sort_key,
                                      'limit': MAX_BODY_SIZE,
                                      'page': 0,
                                      })
        if state is not None:
            url = update_url_params(url, {'states': state})

        # Checking if Given WidgetID Exists:
        if widget_name is not None:
            url = update_url_params(url, {'targetAddresses': widget_name})
            resp = self.get(url).json()
            resp_model = TargetStatsByCampaignResponse(**resp)
            if not resp_model.elements \
                    and not self._widget_exists(
                        time_interval=kwargs['time_interval'],
                        campaignNameOrId=campaignNameOrId,
                        widget_name=widget_name,
                    ):
                return [], ErrorList([f"No Such Widget Exists: '{widget_name}'"])
            else:
                all_widgets_stats = resp_model.elements
        else:
            all_widgets_stats = []
            num_pages_needed = calc_num_pages(url)
            for page_num in range(num_pages_needed):
                url = update_url_params(url, {'page': page_num})
                resp = self.get(url).json()
                resp_model = TargetStatsByCampaignResponse(**resp)
                # todo validate that only the currect state is returning results
                all_widgets_stats.extend(resp_model.elements)

        merged_widget_data = [TargetStatsMergedData(**widget_data.dict(include={'id', 'target',
                                                                                'source', 'sourceId',
                                                                                'trafficSourceType', 'state'}),
                                                    **widget_data.stats.dict())
                              for widget_data in all_widgets_stats]
        merged_widget_data.sort(key=lambda widget: widget.conversions, reverse=True)
        filtered_sites = merged_widget_data[:int(filter_limit or 1)] if filter_limit else merged_widget_data
        result = filter_result_by_fields(filtered_sites, fields)
        return result

    def widgets_top(self, filter_limit: int = DEFAULT_FILTER_NUMBER, **kwargs) -> List[TargetStatsMergedData]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        return self.widgets_stats(filter_limit=filter_limit, sort_key='CONVERSIONS', **kwargs)

    @fields_list_hook(TargetStatsMergedData)
    def widgets_filter_cpa(self, *,
                           threshold: float,
                           operator: Literal['eq', 'ne', 'lt', 'gt', 'le', 'ge'] = 'le',
                           fields: List[str] = ['target', 'spent', 'conversions', 'ecpa'],
                           **kwargs,
                           ) -> List[TargetStatsMergedData]:
        """
        Get list of all the widgets (Where Conversions > 1) of a given {campaignNameOrId}
        which had CPA of less than {threshold}
        """
        if 'filter_limit' in kwargs:
            del kwargs['filter_limit']
        widgets_stats = self.widgets_stats(sort_key='SPENT', **kwargs)
        filtered_by_conversions = [stat for stat in widgets_stats if stat['conversions'] > 0]
        filtered_by_cpa = [stat for stat in filtered_by_conversions
                           # the operator is used here:
                           if getattr(stat['ecpa'], OPERATORS_MAP[operator])(float(threshold))]
        result = filter_result_by_fields(filtered_by_cpa, fields)
        return result

    def widgets_high_cpa(self, **kwargs) -> List[TargetStatsMergedData]:
        return self.widgets_filter_cpa(operator='ge', **kwargs)

    def widgets_low_cpa(self, **kwargs) -> List[TargetStatsMergedData]:
        return self.widgets_filter_cpa(operator='le', **kwargs)

    def _validate_widget_filter_resp(self, resp):
        if not resp.is_json:
            raise APIError(
                platform='ZeroPark',
                data={**resp.json(),
                      'url': resp.url,
                      'reason': resp.reason,
                      'errors': resp.content,
                      'status_code': resp.status_code},
                explain=resp.reason
            )

    @alias_param_campaignNameOrId
    def widgets_turn_on_all(self, campaignNameOrId: str, **kwargs) -> dict:
        kwargs.update({
            'campaignNameOrId': campaignNameOrId,
            'fields': ['target'],
            'time_interval': DEFAULT_TIME_INTERVAL,
            'state': 'PAUSED',
        })
        paused_widgets = self.widgets_stats(**kwargs)
        widgets_names = [w['target'] for w in paused_widgets]
        url = urls.WIDGETS.RESUME.format(campaign_id=campaignNameOrId)
        for chunk_widgets_names in chunks(widgets_names, MAX_URL_PARAMS_SIZE):
            url = update_url_params(url, {'hashOrAddress': ','.join(chunk_widgets_names)})
            resp = self.post(url)
            self._validate_widget_filter_resp(resp)
        return {
            'Success': True,
            'Action': f'Turned On {len(paused_widgets)} Widgets',
            'Data': f'Campaign: {campaignNameOrId}',
        }

    @alias_param_campaignNameOrId
    def widgets_kill_longtail(self, *,
                              campaignNameOrId: str,
                              threshold: float,
                              **kwargs,
                              ) -> dict:
        kwargs.update({
            'campaignNameOrId': campaignNameOrId,
            'fields': ['target', 'spent', 'state'],
            'time_interval': DEFAULT_TIME_INTERVAL,
        })
        active_widgets_stats = self.widgets_stats(sort_key='SPENT', state='ACTIVE', **kwargs)
        widgets_names_filtered_by_spent = [widget['target'] for widget in active_widgets_stats
                                           if widget['spent'] < float(threshold)]

        url = urls.WIDGETS.PAUSE.format(campaign_id=campaignNameOrId)
        for chunk_widgets_names in chunks(widgets_names_filtered_by_spent, MAX_URL_PARAMS_SIZE):
            url = update_url_params(url, {'hashOrAddress': ','.join(chunk_widgets_names)})
            resp = self.post(url)
            self._validate_widget_filter_resp(resp)
        return {
            'Success': True,
            'Action': f'Paused {len(active_widgets_stats)} Widgets',
            'Data': f'Campaign: {campaignNameOrId}',
        }

    def widget_kill_bot_traffic(self, *,
                                campaignNameOrId: str,
                                threshold: float,
                                **kwargs,) -> list:
        pass
