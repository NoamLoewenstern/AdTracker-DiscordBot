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
            self.campaigns[campaign.campId] = campaign.name

    def _update_sources_cache(self, updated_sources: List[Source]):
        for source in updated_sources:
            self.sources[source.sourceId] = source.name

    def list_campaigns(self,
                       extra_query_args: Optional[Dict[Union['search',
                                                             'all'], Union[str, int]]] = None,
                       fields: Optional[List[Union['name', 'id']]] = ['name', 'id']) -> list:
        result = []
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS
        url = update_url_params(url, extra_query_args)
        resp = self.get(url).json()
        resp_model = CampaignGETResponse(**resp)
        self._update_campaigns_cache(resp_model.data)
        for campaignNameID in resp_model.data:
            elem_filtered_data = {}
            elem_filtered_data.update({
                'id': campaignNameID.campId,
                'name': campaignNameID.name,
            })
            result.append(elem_filtered_data)
        return result

    def list_sources(self,
                     extra_query_args: Optional[Dict[Union['search',
                                                           'all'], Union[str, int]]] = None,
                     fields: Optional[List[Union['name', 'id']]] = ['name', 'id']) -> list:
        result = []
        url = urls.CAMPAIGNS.LIST_SOURCES
        url = update_url_params(url, extra_query_args)
        resp = self.get(url).json()
        resp_model = SourceGETResponse(**resp)
        self._update_sources_cache(resp_model.data)
        for source in resp_model.data:
            elem_filtered_data = {}
            elem_filtered_data.update({
                'id': source.sourceId,
                'name': source.name,
            })
            result.append(elem_filtered_data)
        return result
