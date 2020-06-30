import json
# import os
import logging
import re
from typing import Callable, Dict, List, Optional, Union

from errors import InvalidCampaignId, InvalidPlatormCampaignName
# from services.thrive import Thrive
from utils import alias_param, append_url_params, update_url_params

from ..common import CommonService
from ..thrive.schemas import CampaignExtendedInfoStats
from . import urls
from .parameter_enums import DateIntervalParams
from .schemas import (CampaignBaseData, CampaignData, CampaignGETResponse,
                      CampaignStat, CampaignStatDayDetailsGETResponse,
                      MergedWithThriveStats, StatsAllCampaignGETResponse)
from .utils import (ConvertKeyToIntDict, add_token_to_uri,
                    fix_date_interval_value, get_thrive_id_from_camp,
                    update_client_id_in_uri)


class MGid(CommonService):
    # TODO check different types of statuses - to filter out the deleted ones
    def __init__(self, client_id: str, token: str, thrive):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL,
                         uri_hooks=[
                             lambda uri: add_token_to_uri(uri, token),
                             lambda uri: update_client_id_in_uri(uri, client_id)
                         ])
        self.__campaigns: Dict[int, str] = {}  # id: name
        self.thrive = thrive

    @property
    def campaigns(self):
        if not self.__campaigns:
            filter_fields = ['id', 'name', 'status', 'statistics']
            url = urls.CAMPAIGNS.LIST_CAMPAIGNS
            url = append_url_params(url, {'fields': json.dumps(filter_fields, separators=(',', ':'))})
            resp = self.get(url).json()
            resp_model = CampaignGETResponse.parse_obj(resp)
            campaigns = resp_model.__root__.values()

            self.__campaigns = {campaign.id: campaign for campaign in campaigns}
            self.__campaigns = ConvertKeyToIntDict(self.campaigns)
        return self.__campaigns

    @campaigns.setter
    def campaigns(self, value):
        if isinstance(value, dict):
            value = ConvertKeyToIntDict(value)
        self.__campaigns = value

    def _removed_deleted(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]):
        return [camp for camp in campaigns if camp['id'] in self.campaigns]

    def _add_names_to_campaigns_values(self, campaigns: List[Union[CampaignBaseData, Dict['id', str]]]):
        for camp in campaigns:
            camp['name'] = self.campaigns[camp['id']].name
        return campaigns

    def list_campaigns(self,
                       limit: int = None,
                       start: int = None,
                       campaign_id: int = None,
                       fields: List[str] = ['name', 'id'],
                       **kwargs) -> list:
        result = []
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS
        if campaign_id is not None:
            url = urls.CAMPAIGNS.LIST_CAMPAIGNS + '/' + str(campaign_id)
        if limit and start is not None:
            url = update_url_params(url, {'limit': limit, 'start': start})
        if fields:
            url = append_url_params(url, {'fields':  json.dumps(fields, separators=(',', ':'))})
        resp = self.get(url).json()
        if campaign_id is None:
            resp_model = CampaignGETResponse.parse_obj(resp)
            campaigns = resp_model.__root__.values()
        else:
            resp_model = CampaignData(**resp)
            campaigns = [resp_model]

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

    def _merge_thrive_stats(self, stats: List['CampaignStat.dict'],
                            thrive_results: List['CampaignExtendedInfoStats.dict']) -> list:
        merged = []
        for stat in stats:
            camp_thrive_id = get_thrive_id_from_camp(stat)
            for thrive_result in thrive_results:
                if str(camp_thrive_id) == str(thrive_result['id']):
                    logging.debug(f"->\tMGID stats: {stat}\n\tTHRIVE stats: {thrive_result}")
                    # stat.update({**thrive_result, 'id': stat['id']})
                    merged_dict = {**thrive_result, **stat.dict()}
                    merged.append(MergedWithThriveStats(**merged_dict))
                    logging.debug(f"\tMERGED stats: {stat}")
        return merged

    @alias_param(alias='dateInterval', key='time_interval',
                 callback=lambda value: fix_date_interval_value(value.lower()))
    def stats_all_campaigns(self, *,
                            dateInterval: DateIntervalParams = 'today',
                            fields: Optional[List] = ['id', 'name', 'click', 'cost', 'conv',
                                                      'cpa', 'roi', 'revenue', 'profit'],  # CampaignStat
                            # revenue <- rev, profit'],  # CampaignStat
                            **kwargs) -> List['CampaignStat.dict']:
        url = urls.CAMPAIGNS.STATS_DAILY
        url = update_url_params(url, {'dateInterval': dateInterval})
        resp = self.get(url).json()
        resp_model = StatsAllCampaignGETResponse(**resp)
        stats = resp_model.campaigns_stat.values()
        stats = self._removed_deleted(stats)
        self._add_names_to_campaigns_values(stats)
        tracker_result = self.thrive.stats_campaigns(time_interval=kwargs.get('time_interval'))
        merged_stats = self._merge_thrive_stats(stats, tracker_result)
        if fields is None:
            result = [stat.dict() for stat in merged_stats]
        else:
            result = []
            for stat in merged_stats:
                result.append({field: getattr(stat, field) for field in fields if hasattr(stat, field)})
        # result = self._add_names_to_campaigns_values(result)
        return result

    def stats_campaign(self, campaign_id=None, **kwargs) -> list:
        result: List[CampaignStat.dict] = self.stats_all_campaigns(**kwargs)
        if campaign_id is not None:  # returning list of all campaigns.
            result = [camp for camp in result if str(camp['id']) == campaign_id]
        # thrive_camp_id = self.campaigns[campaign_id].thrive_id if campaign_id else None
        # tracker_result = self.thrive.stats_campaigns(campaign_id=thrive_camp_id,
        #                                              time_interval=kwargs.get('time_interval'))
        # merged_results = self._merge_thrive_stats(result, tracker_result)
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
