# import os
import json
import logging
from typing import Callable, Dict, List, Optional, Union

from errors import InvalidCampaignId
from utils import alias_param, append_url_params, update_url_params

from ..common import CommonService
from . import urls
from .parameter_enums import DateIntervalParams
from .schemas import (CampaignData, CampaignGETResponse, CampaignStat,
                      CampaignStatDayDetailsGETResponse,
                      StatsAllCampaignGETResponse)
from .utils import (add_token_to_uri, fix_date_interval_value,
                    update_client_id_in_uri)


class MGid(CommonService):
    # TODO check different types of statuses - to filter out the deleted ones
    def __init__(self, client_id: str, token: str):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL,
                         uri_hooks=[
                             lambda uri: add_token_to_uri(uri, token),
                             lambda uri: update_client_id_in_uri(uri, client_id)
                         ])
        self.__campaigns: Dict[int, str] = {}  # id: name

    @property
    def campaigns(self):
        if not self.__campaigns:
            self.list_campaigns()
        return self.__campaigns

    @campaigns.setter
    def campaigns(self, value):
        self.__campaigns = value

    def _update_campaigns_cache(self, updated_campaigns: List[CampaignData]):
        self.campaigns = {campaign.id: campaign.name for campaign in updated_campaigns}

    def list_campaigns(self,
                       limit: int = None,
                       start: int = None,
                       fields: List[str] = ['name', 'id'],
                       **kwargs) -> list:
        result = []
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS
        if limit and start is not None:
            url = update_url_params(url, {'limit': limit, 'start': start})
        if fields:
            url = append_url_params(url, {'fields':  json.dumps(fields, separators=(',', ':'))})
        resp = self.get(url).json()
        resp_model = CampaignGETResponse.parse_obj(resp)
        campaigns = resp_model.__root__.values()
        self._update_campaigns_cache(campaigns)
        for campaign in campaigns:
            result.append({field: getattr(campaign, field)
                           for field in fields if hasattr(campaign, field)})

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

    @alias_param(alias='dateInterval', key='time_interval',
                 callback=lambda value: fix_date_interval_value(value.lower()))
    def stats_all_campaigns(self, *,
                            dateInterval: DateIntervalParams = 'today',
                            fields: Optional[List] = None,  # CampaignStat
                            **kwargs) -> list:
        url = urls.CAMPAIGNS.STATS_DAILY
        url = update_url_params(url, {'dateInterval': dateInterval})
        resp = self.get(url).json()
        resp_model = StatsAllCampaignGETResponse(**resp)
        if fields is None:
            result = [stats.dict() for stats in resp_model.campaigns_stat.values()]
        else:
            result = []
            for _id, stats in resp_model.campaigns_stat.items():
                result.append({field: getattr(stats, field) for field in fields if hasattr(stats, field)})
        return result

    def stats_campaign(self, campaign_id=None, *args, **kwargs) -> list:
        result = self.stats_all_campaigns(*args, **kwargs)
        if campaign_id is None:
            return result  # returning list of all campaigns.
        result = [camp_data for camp_data in result if str(camp_data['id']) == campaign_id]
        return result

    def spent_campaign(self, campaign_id=None, min_spent=0.0001, *args, **kwargs) -> list:
        kwargs.setdefault('fields', ['id', 'spent'])
        results = self.stats_campaign(campaign_id=campaign_id,
                                      *args, **kwargs)
        filtered_results = []
        for result in results:
            try:
                if result['spent'] >= min_spent:
                    filtered_results.append({'id': result['id'],
                                             'name': self.campaigns[result['id']],
                                             'spent': result['spent']})
            except KeyError as e:
                logging.warning(f"KeyError: ID {result['id']} not listed in campaign-list\nError: {e}")
        return filtered_results
