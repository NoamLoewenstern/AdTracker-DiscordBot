from typing import Callable, List, Optional, Union

from utils import append_url_params, update_url_params

from ..common import CommonService
from . import urls
from .schemas import CampaignStatsResponse


def filter_campaign_data(element: dict, fields: list):
    pass


class ZeroPark(CommonService):
    def __init__(self, token: str):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL)
        self.session.headers.update({'api-token': token})

    def list_campaigns(self,
                       extra_query_args: Optional[dict] = None,
                       fields: Optional[List[str]] = ['name', 'id']) -> list:
        result = []
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS

        if extra_query_args:
            url = update_url_params(url, extra_query_args)
        resp = self.get(url).json()
        resp_model = CampaignStatsResponse(**resp)
        for elem in resp_model.elements:
            elem_filtered_data = {}
            elem_filtered_data.update({
                'id': elem.details.id,
                'name': elem.details.name,
            })
            result.append(elem_filtered_data)
        return result
