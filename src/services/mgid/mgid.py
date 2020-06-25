# import os
import logging
from typing import Callable, List, Optional, Union

from utils import append_url_params, update_url_params

from ..common import CommonService
from . import urls
from .utils import add_token_to_uri, update_client_id_in_uri


class MGid(CommonService):
    def __init__(self, client_id: str, token: str):
        super().__init__(base_url=urls.CAMPAIGNS.BASE_URL,
                         uri_hooks=[
                             lambda uri: add_token_to_uri(uri, token),
                             lambda uri: update_client_id_in_uri(uri, client_id)
                         ])
        # self.client_id: str = client_id
        # self.token: str = token

    def list_campaigns(self,
                       extra_query_args: Optional[dict] = None,
                       fields: Optional[List[str]] = ['name', 'id']) -> list:
        result = []
        url = urls.CAMPAIGNS.LIST_CAMPAIGNS
        if extra_query_args:
            url = update_url_params(url, extra_query_args)
        if fields:
            url = append_url_params(url, {'fields': fields})
        resp = self.get(url).json()
        for _id, content in resp.items():
            result.append({field: content[field] for field in fields})
        return result
