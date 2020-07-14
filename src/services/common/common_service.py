import logging
from enum import Enum
from typing import Callable, List, Optional, Union

import requests

from constants import DEFAULT_TIMEOUT_API_REQUEST
from errors import APIError


class TargetType(str, Enum):
    DESKTOP = 'DESKTOP'
    MOBILE = 'MOB'
    BOTH = 'BOTH'


class CommonService:
    def __init__(self, base_url: str, uri_hooks: Optional[List[Callable[[str], str]]] = None):
        self.base_url = base_url
        self.session = self.__init_session()
        self.uri_hooks = uri_hooks if uri_hooks else []

    def __init_session(self):
        session = requests.Session()
        session.headers.update({'Accept': 'application/json'})
        return session

    def _req(self,
             uri: str,
             method: Union['get', 'post', 'put', 'patch', 'delete'],
             *args: list,
             **kwargs: dict):
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT_API_REQUEST)
        for uri_hook in self.uri_hooks:
            uri = uri_hook(uri)
        logging.info(f'[REQ] [{method.upper()}] {self.base_url + uri}')
        resp = getattr(self.session, method)(self.base_url + uri, *args, **kwargs)
        if 'application/json' not in resp.headers['Content-Type']:
            logging.error('[!] unexpected resp: is not json')
        if not resp.ok:
            raise APIError(platform='',
                           data={**resp.json(),
                                 'url': self.base_url + uri,
                                 'reason': resp.reason,
                                 'status_code': resp.status_code},
                           explain=resp.reason)
        return resp

    def get(self, uri: str, *args, **kwargs):
        return self._req(uri, 'get', *args, **kwargs)

    def post(self, uri: str, *args, **kwargs):
        return self._req(uri, 'post', *args, **kwargs)

    def put(self, uri: str, *args, **kwargs):
        return self._req(uri, 'put', *args, **kwargs)

    def patch(self, uri: str, *args, **kwargs):
        return self._req(uri, 'patch', *args, **kwargs)

    def delete(self, uri: str, *args, **kwargs):
        return self._req(uri, 'delete', *args, **kwargs)
