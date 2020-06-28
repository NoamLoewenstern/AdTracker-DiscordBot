from typing import List, Optional, Union

from utils import alias_param, append_url_params, update_url_params

from ..common import CommonService
from . import urls
from .schemas import CampaignStatsResponse
from .utils import fix_date_interval_value


class ZeroPark(CommonService):
    # TODO check different types of statuses - to filter out the deleted ones
    def __init__(self, token: str):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL)
        self.session.headers.update({'api-token': token})

    @alias_param(alias='interval', key='time_interval',
                 callback=lambda value: fix_date_interval_value(value))
    def list_campaigns(self,
                       interval: str = "TODAY",
                       fields: Optional[List[str]] = ['name', 'id']) -> list:
        result = []
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS
        url = update_url_params(url, {'interval': interval})
        resp = self.get(url).json()
        resp_model = CampaignStatsResponse(**resp)

        for elem in resp_model.elements:
            result.append({field: elem[field] for field in fields})
        return result
