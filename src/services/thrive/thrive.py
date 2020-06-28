# import os
from typing import Callable, Dict, List, Optional, Union

from utils import append_url_params, update_url_params

from ..common import CommonService
from . import urls
from .schemas import (CampaignGETResponse, CampaignNameID, Source, SourceBase,
                      SourceCache, SourceGETResponse)


class Thrive(CommonService):
    def __init__(self, apiKey: str, installId: str):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL)
        self.session.headers.update({'apiKey': apiKey, 'installId': installId})
        self.campaigns: Dict[int, str] = {}
        self.sources: Dict[int, str] = {}

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
        result = []
        for campaignNameID in resp_model.data:
            result.append({field: getattr(campaignNameID, field) for field in fields if hasattr(campaignNameID, field)})
        return result

    def list_sources(self, *,
                     search: str = '',
                     camps: Optional[bool] = True,
                     all: Optional[bool] = True,
                     back: Optional[bool] = None,
                     fields: List[Union['name', 'id', 'campCount']] = ['name', 'id', 'campCount'],
                     **kwargs) -> list:
        result = []
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
        for source in resp_model.data:
            result.append({field: getattr(source, field) for field in fields if hasattr(source, field)})
        return result
