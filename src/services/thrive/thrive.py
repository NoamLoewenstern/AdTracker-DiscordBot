# import os
import logging
from typing import Dict, List, Optional, Union

from utils import (alias_param, append_url_params, filter_result_by_fields,
                   update_url_params)

from ..common import CommonService
from ..common.utils import add_interval_startend_dates
from . import urls
from .config import WIDGET_KEYS_MAPPER
from .schemas import (
    CampaignGeneralInfo, CampaignGETResponse, CampaignNameID, CampaignStats,
    Source, SourceGETResponse, WidgetStats, WidgetStatsGETResponse)
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
                       fields: List[Union['name', 'id', 'source']] = ['name', 'id', 'source'],
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
                     fields: List[Union['name', 'id', 'campCount']] = ['name', 'id', 'campCount'],
                     **kwargs) -> list:
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
        url = urls.CAMPAIGNS.CAMPAIGN_INFO
        url = update_url_params(url, {'campId': campaign_id})
        resp = self.get(url).json()
        resp_model = CampaignGeneralInfo(**resp)
        # self._update_sources_cache(resp_model.data)
        result = filter_result_by_fields(resp_model.data, fields)
        return result

    @adjust_interval_params
    def stats_campaigns(self, *,
                        campaign_id: Optional[str] = None,
                        interval: str = '1d',
                        fields: List[str] = ['name', 'id', 'clicks', 'thrive_clicks',
                                             'cost', 'conv', 'ctr', 'roi', 'rev', 'profit', 'cpa'],
                        **kwargs) -> List['CampaignExtendedInfoStats.dict']:
        url = urls.CAMPAIGNS.CAMPAIGN_STATS
        if campaign_id:
            url = update_url_params(url, {'camps': campaign_id})
        url = append_url_params(url, {'range[from]': kwargs['startDate'],
                                      'range[to]': kwargs['endDate']})
        # TODO implement the 'time_range' for request.
        # it has some problems.
        resp = self.get(url).json()
        resp_model = CampaignStats(**resp)
        result = filter_result_by_fields(resp_model.data, fields)
        return result

    def _remove_unknown_ids(self, list_objects: List[Dict['id', str]], platform='') -> None:
        unknown_widgets_ids = []
        for i, widget_stat in enumerate(list_objects):
            if widget_stat['id'] == 'unknown':
                unknown_widgets_ids.append(list_objects.pop(i))
        if unknown_widgets_ids:
            logging.error(f'[thrive] [widgets_stats] [platform:{platform}] '
                          f'{len(unknown_widgets_ids)} Unknown Widgets.')
        return unknown_widgets_ids

    def _convert_subids_to_uids(self, list_objects: List[Dict['id', str]]) -> List[Dict['id', str]]:
        return subids_to_uids(list_objects)

    @adjust_interval_params
    def _widgets_stats(self, *,
                       platform_name: str,
                       campaign_id: str,
                       widget_id: str = None,
                       interval: str = '1d',
                       sort_key: str = 'conv',
                       fields: List[str] = ['id', 'clicks', 'cost', 'conv',
                                            'cpc', 'cpa', 'rev', 'profit'],
                       **kwargs,
                       ) -> List[WidgetStats]:
        assert platform_name.lower() in WIDGET_KEYS_MAPPER, \
            f"'platform_name' must be of types: {list(WIDGET_KEYS_MAPPER.keys())}"
        assert sort_key in WidgetStats.__fields__.keys(), \
            f"'sort_key' must be of types: {list(WidgetStats.__fields__.keys())}"
        url = urls.WIDGETS.LIST
        url = append_url_params(url, {'camps': campaign_id,
                                      'range[from]': kwargs['startDate'] or '',
                                      'range[to]': kwargs['endDate'] or '',
                                      'key': WIDGET_KEYS_MAPPER[platform_name.lower()]})
        resp = self.get(url).json()
        resp_model = WidgetStatsGETResponse.parse_obj(resp)
        resp_model.__root__.sort(key=lambda widget: widget[sort_key])
        # self._remove_unknown_ids(resp_model.__root__)

        result = filter_result_by_fields(resp_model.__root__, fields)
        return result
