# import os
from typing import Dict, List, Literal, Optional, Union

from errors import ErrorDict
from logger import logger
from services.common.common_service import TargetType

from utils import alias_param, append_url_params, update_url_params
from utils.helpers import merge_objs

from ..common import CommonService
from ..common.utils import add_interval_startend_dates, filter_result_by_fields
from . import urls
from .config import CAMP_STATS_VARIABLE_TYPES, STATS_BY_VARIABLE_MAPPER
from .schemas import (CampaignGeneralInfo, CampaignGETResponse,
                      CampaignInfoAndStats, CampaignInfoAndStatsResponse,
                      CampaignMetricsStatsResponse, CampaignNameID,
                      CampaignStats, CampaignStatsByDevice,
                      CampaignStatsResponse, Source, SourceGETResponse)
from .utils import fix_date_interval_value, subids_to_uids


def adjust_interval_params(func):
    alias_param_interval = alias_param(
        alias='interval',
        key='time_interval',
        callback=lambda value: fix_date_interval_value(value.lower()) if value else value
    )
    add_startend_dates_by_interval = add_interval_startend_dates(
        'interval',
        custom_date_key='interval',
        strftime=r'%m/%d/%Y')
    return alias_param_interval(add_startend_dates_by_interval(func))


class Thrive(CommonService):
    def __init__(self, apiKey: str, installId: str):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL)
        self.session.headers.update({'apiKey': apiKey, 'installId': installId})
        self.campaigns: Dict[int, str] = {}
        self.sources: Dict[int, str] = {}
        self.platforms: List[CommonService] = []  # : List[PlatformService]

    def _update_campaigns_cache(self, updated_campaigns: List[CampaignNameID]):
        for campaign in updated_campaigns:
            self.campaigns[campaign.id] = campaign.name

    def _update_sources_cache(self, updated_sources: List[Source]):
        for source in updated_sources:
            self.sources[source.id] = source.name

    def list_campaigns(self,
                       search: str = None,
                       fields: List[Literal['name', 'id', 'source']] = ['name', 'id', 'source'],
                       **kwargs) -> list:
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS
        if search:
            url = update_url_params(url, {'search': search})
        resp = self.get(url).json()
        resp_model = CampaignGETResponse(**resp)
        self._update_campaigns_cache(resp_model.data)
        result = filter_result_by_fields(resp_model.data, fields)
        return result

    def list_sources(self, *,
                     search: str = '',
                     camps: Optional[bool] = True,
                     all: Optional[bool] = True,
                     back: Optional[bool] = None,
                     fields: List[Literal['name', 'id', 'campCount']] = ['name', 'id', 'campCount'],
                     **kwargs) -> List[Source]:
        url = urls.CAMPAIGNS.LIST_SOURCES
        if search:
            url = update_url_params(url, {'search': search})
        if back:
            url = update_url_params(url, {'back': back})
        url = update_url_params(url, {
            'camps': camps,
            'all': all,
        })
        resp = self.get(url).json()
        resp_model = SourceGETResponse(**resp)
        self._update_sources_cache(resp_model.data)
        result = filter_result_by_fields(resp_model.data, fields)
        return result

    def info_campaign(self, *,
                      campaign_id: str,
                      fields: List[str] = ['name', 'id', 'sourceName', 'campCount'],
                      **kwargs) -> list:
        url = urls.CAMPAIGNS.GENERAL_INFO
        url = update_url_params(url, {'campId': campaign_id})
        resp = self.get(url).json()
        resp_model = CampaignGeneralInfo(**resp)
        # self._update_sources_cache(resp_model.data)
        result = filter_result_by_fields(resp_model.data, fields)
        return result

    @adjust_interval_params
    def info_and_stats_campaign(self, *,
                                campaign_id: str = None,
                                interval: str = '1d',
                                startDate: str,
                                endDate: str,
                                fields: List[str] = ['name', 'id', 'clicks', 'thrive_clicks',
                                                     'cost', 'conv', 'ctr', 'roi', 'rev', 'profit', 'cpa'],
                                **kwargs) -> List[CampaignInfoAndStats]:
        url = urls.CAMPAIGNS.GENERAL_INFO_WITH_STATS
        if campaign_id:
            url = update_url_params(url, {'camps': campaign_id})
        url = append_url_params(url, {'range[from]': startDate,
                                      'range[to]': endDate})
        # TODO implement the 'time_range' for request.

        resp = self.get(url).json()
        resp_model = CampaignInfoAndStatsResponse(**resp)
        result = filter_result_by_fields(resp_model.data, fields)
        return result

    @adjust_interval_params
    def stats_campaigns(self, *,
                        campaign_id: str = None,
                        interval: str = '1d',
                        startDate: str,
                        endDate: str,
                        fields: List[str] = ['name', 'id', 'clicks', 'thrive_clicks',
                                             'cost', 'conv', 'ctr', 'roi', 'rev', 'profit', 'cpa'],
                        **kwargs) -> List[CampaignStats]:
        url = urls.CAMPAIGNS.GENERAL_INFO_WITH_STATS
        if campaign_id:
            url = update_url_params(url, {'camps': campaign_id})
        url = append_url_params(url, {'range[from]': startDate,
                                      'range[to]': endDate})
        # TODO implement the 'time_range' for request.

        resp = self.get(url).json()
        resp_model = CampaignInfoAndStatsResponse(**resp)
        result = filter_result_by_fields(resp_model.data, fields)
        return result

    @adjust_interval_params
    def stats_campaigns_by_variable(self, *,
                                    campaign_id: str = None,
                                    interval: str = '1d',
                                    startDate: str,
                                    endDate: str,
                                    key: CAMP_STATS_VARIABLE_TYPES,
                                    sort_key: str = 'conv',
                                    fields: List[str] = ['id', 'name', 'value', 'period', 'clicks', 'thrive_clicks', 'cost', 'cpc',
                                                         'thru', 'conv', 'rev', 'ctr', 'profit', 'roi', 'epc', 'cvr', 'epa', 'cpa'],

                                    **kwargs) -> List[CampaignStats]:
        def validate_input():
            allowed_fields = list(CampaignStats.__fields__)
            assert sort_key in allowed_fields, f"'sort_key' must be of allowed fields: {allowed_fields}"
            assert sort_key in fields, f"'sort_key' must be of allowed fields passed to method: {fields}"
            assert key in STATS_BY_VARIABLE_MAPPER, f'variable type must be type of: {CAMP_STATS_VARIABLE_TYPES}'
        validate_input()

        url = urls.CAMPAIGNS.STATS_BY_VAR
        if campaign_id:
            url = update_url_params(url, {'camps': campaign_id})

        # TODO implement the 'time_range' for request.
        url = append_url_params(url, {'range[from]': startDate,
                                      'range[to]': endDate,
                                      'key': STATS_BY_VARIABLE_MAPPER[key.lower()]})

        resp = self.get(url).json()
        list_stats_model = CampaignStatsResponse.parse_obj(resp).__root__
        if not list_stats_model:
            return []
        list_stats_model.sort(key=lambda widget: widget[sort_key])
        if campaign_id:
            for stat_model in list_stats_model:
                stat_model.id = campaign_id

        result = filter_result_by_fields(list_stats_model, fields)
        return result

    def stats_campaign_by_device_type(self, *,
                                      campaign_id: str,
                                      device: TargetType = TargetType.BOTH,
                                      **kwargs) -> CampaignStatsByDevice:
        assert campaign_id, 'campaign_id must not be empty or None'
        stats: List[CampaignStats] = self.stats_campaigns_by_variable(
            campaign_id=campaign_id,
            key=CAMP_STATS_VARIABLE_TYPES.by_device_type,
            **kwargs)
        if not stats:
            return {}
        if device.lower() == TargetType.BOTH.lower():
            merged_stats = merge_objs(*stats)
            merged_stats['value'] = TargetType.BOTH
            ret_stats = CampaignStatsByDevice(**merged_stats)
        else:
            filtered_stats = [stat for stat in stats
                              if stat['value'].lower() == device.lower()]
            if stats and not filtered_stats:
                raise ValueError('No Device Type "{device}" in Campaign Stats: {stat}')
            filtered_stats = filtered_stats[0]
            filtered_stats['value'] = device.upper()
            ret_stats = CampaignStatsByDevice(**filtered_stats)

        return {
            **ret_stats.dict(),
            'id': campaign_id,
        }

    def stats_widgets(self, *,
                      platform_name: Literal['mgid', 'zeropark'],
                      campaign_id: str,
                      **kwargs) -> List[CampaignStats]:
        def validate_input():
            # if 'key' is 'mgid' or 'zeropark' -> it means that it's searching the WIDGETS data INSIDE campaign.
            # means must come with campaign_id:
            # if key != CAMP_STATS_VARIABLE_TYPES.by_device_type:
            #     assert campaign_id, 'if requesting widgets - must pass campaign_id.'
            platforms = ['mgid', 'zeropark']
            assert platform_name.lower() in platforms, \
                f"'platform_name' passed by 'key' must be of types: {platforms}"
        validate_input()
        platform_widgets_var_type: CAMP_STATS_VARIABLE_TYPES
        platform_widgets_var_type = getattr(CAMP_STATS_VARIABLE_TYPES, f'{platform_name.lower()}_widgets')
        widgets_stats: List[CampaignStats] = self.stats_campaigns_by_variable(campaign_id=campaign_id,
                                                                              key=platform_widgets_var_type,
                                                                              **kwargs)
        # self._remove_unknown_ids(resp_model.__root__)

        return widgets_stats

    def _remove_unknown_ids(self, list_objects: List[Dict['id', str]], platform='') -> None:
        unknown_widgets_ids = []
        for i, widget_stat in enumerate(list_objects):
            if widget_stat['id'] == 'unknown':
                unknown_widgets_ids.append(list_objects.pop(i))
        if unknown_widgets_ids:
            logger.warning(f'[thrive] [widgets_stats] [platform:{platform}] '
                           f'{len(unknown_widgets_ids)} Unknown Widgets.')
        return unknown_widgets_ids

    def _convert_subids_to_uids(self, list_objects: List[Dict['id', str]]) -> List[Dict['id', str]]:
        return subids_to_uids(list_objects)
