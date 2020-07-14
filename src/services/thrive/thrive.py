# import os
from typing import Callable, Dict, List, Optional, Union

from utils import (alias_param, append_url_params, filter_result_by_fields,
                   update_url_params)

from ..common import CommonService
from ..common.utils import add_interval_startend_dates
from . import urls
from .schemas import (
    CampaignGeneralInfo, CampaignGETResponse, CampaignNameID, CampaignStats,
    Source, SourceGETResponse)
from .utils import fix_date_interval_value

source_mapper = {
    3: 'MGID',
    7: 'ZeroPark',
}


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
                        time_interval: str = '1d',
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
