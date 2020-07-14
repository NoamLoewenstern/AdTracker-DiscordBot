import logging
from typing import Any, Dict, List, Optional, Union

# from extensions import Thrive
from utils import (DictForcedStringKeys, alias_param, append_url_params,
                   filter_result_by_fields, operator_factory,
                   update_url_params)

from ..common.platform import PlatformService
from ..common.utils import add_interval_startend_dates
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
            campaigns = self.list_campaigns(fields=['id', 'name', 'clicks',
                                                    'spent', 'bid', 'target_type'])
            self._campaigns = self._update_campaigns(campaigns)
        return self._campaigns

    def list_campaigns(self,
                       fields: Optional[List[str]] = ['id', 'name'],
                       **kwargs) -> list:
        stats = self.stats_campaign_pure_platform(**kwargs)
        stats = filter_result_by_fields(stats, fields)
        return stats

    @adjust_interval_params
    @alias_param_campaignNameOrId
    def stats_campaign_pure_platform(self,
                                     campaignNameOrId: str = None,
                                     interval: str = "TODAY",
                                     as_json=True,
                                     **kwargs) -> list:
        url = urls.CAMPAIGNS.STATS
        url = update_url_params(url, {'interval': interval,
                                      'startDate': kwargs.get('startDate', ''),
                                      'endDate': kwargs.get('endDate', '')})
        if campaignNameOrId is not None:
            url = update_url_params(url, {'campaignNameOrId': campaignNameOrId})
        resp = self.get(url).json()
        resp_model = CampaignStatsResponse(**resp)
        result = extended_stats = ListExtendedStats.parse_obj(
            [ExtendedStats(**elem.stats.dict(), **elem.details.dict())
             for elem in resp_model.elements]).__root__
        if campaignNameOrId is not None:  # returning specific campaign
            result = [stat for stat in extended_stats
                      if campaignNameOrId in (stat['id'], stat['name'])]
        else:
            self._update_campaigns(result)
        if as_json:
            result = [stat.dict() for stat in result]
        return result

    @alias_param_campaignNameOrId
    def stats_campaign(self,
                       campaignNameOrId: str = None,
                       fields: Optional[List[str]] = ['id', 'name', 'clicks', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit'],
                       **kwargs) -> List['MergedWithThriveStats.dict']:
        kwargs.update({
            'campaignNameOrId': campaignNameOrId,
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
        result = filter_result_by_fields(merged_stats, fields)
        return result

    def spent_campaign(self, *,
                       min_spent=0.0001,
                       fields: List[str] = ['name', 'id', 'spent'],
                       **kwargs) -> list:
        kwargs.update({'fields': fields})
        stats = self.stats_campaign_pure_platform(**kwargs)
        filtered_by_spent = [stat for stat in stats if stat['spent'] >= min_spent]
        result = filter_result_by_fields(filtered_by_spent, fields)
        return result

    def bot_traffic(self, *,
                    fields: List[str] = ['name', 'id', 'thrive_clicks', 'platform_clicks'],
                    **kwargs) -> list:
        stats = self.stats_campaign(fields=fields, **kwargs)
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

    @adjust_interval_params
    @alias_param_campaignNameOrId
    def widgets_stats(self, *,
                      campaignNameOrId: str,
                      interval: str = "TODAY",
                      widget_name: str = None,
                      filter_limit: int = '',
                      sort_key: str = 'CONVERSIONS',
                      fields: List[str] = ['id', 'target', 'spent', 'conversions', 'ecpa'],
                      **kwargs) -> List[TargetStatsMergedData]:

        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        url = urls.CAMPAIGNS.LIST_WIDGETS.format(campaign_id=campaignNameOrId)
        url = update_url_params(url, {'campaignId': campaignNameOrId,
                                      'interval': interval,
                                      'startDate': kwargs.get('startDate', ''),
                                      'endDate': kwargs.get('endDate', ''),
                                      'sortColumn': sort_key,

                                      'limit': filter_limit,
                                      })
        if widget_name is not None:
            url = update_url_params(url, {'targetAddresses': widget_name})

        resp = self.get(url).json()
        resp_model = TargetStatsByCampaignResponse.parse_obj(resp)

        merged_widget_data = [TargetStatsMergedData(**widget_data.dict(include={'id', 'target',
                                                                                'source', 'sourceId',
                                                                                'trafficSourceType'}),
                                                    **widget_data.stats.dict())
                              for widget_data in resp_model.elements]
        merged_widget_data.sort(key=lambda widget: widget.conversions, reverse=True)
        filtered_sites = merged_widget_data[:int(filter_limit)] if filter_limit else merged_widget_data
        result = filter_result_by_fields(filtered_sites, fields)
        return result

    def widgets_top(self, **kwargs) -> List[TargetStatsMergedData]:
        """
        Get top widgets (sites) {filter_limit} conversions (buy) by {campaign_id}
        """
        return self.widgets_stats(**kwargs)

    def widgets_filter_cpa(self, *,
                           threshold: str,
                           operator: Union['eq', 'ne', 'lt', 'gt', 'le', 'ge'] = 'le',
                           fields: List[str] = ['id', 'target', 'spent', 'conversions', 'ecpa'],
                           **kwargs,
                           ) -> List[TargetStatsMergedData]:
        """
        Get list of all the widgets (Where Conversions > 1) of a given {campaignNameOrId}
        which had CPA of less than {threshhold}
        """
        if 'filter_limit' in kwargs:
            del kwargs['filter_limit']
        widgets_stats = self.widgets_stats(sort_key='SPENT', **kwargs)
        filtered_by_conversions = [stat for stat in widgets_stats if stat['conversions'] > 0]
        filtered_by_cpa = [stat for stat in filtered_by_conversions
                           # the operator is used here:
                           if getattr(stat['ecpa'], operator_factory[operator])(float(threshold))]
        result = filter_result_by_fields(filtered_by_cpa, fields)
        return result

    def widgets_high_cpa(self, **kwargs) -> List[TargetStatsMergedData]:
        return self.widgets_filter_cpa(operator='ge', **kwargs)

    def widgets_low_cpa(self, **kwargs) -> List[TargetStatsMergedData]:
        return self.widgets_filter_cpa(operator='le', **kwargs)

