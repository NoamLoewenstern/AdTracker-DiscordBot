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
    def __init__(self, base_url: str, url_hooks: Optional[List[Callable[[str], str]]] = None):
        self.base_url = base_url
        self.session = self.__init_session()
        self.url_hooks = url_hooks if url_hooks else []

    def __init_session(self):
        session = requests.Session()
        session.headers.update({'Accept': 'application/json'})
        return session

    def _req(self,
             url: str,
             method: Union['get', 'post', 'put', 'patch', 'delete'],
             *args: list,
             **kwargs: dict):
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT_API_REQUEST)
        for url_hook in self.url_hooks:
            url = url_hook(url)
        logging.info(f'[REQ] [{method.upper()}] {self.base_url + url}')
        resp = getattr(self.session, method)(self.base_url + url, *args, **kwargs)
        resp.is_json = 'application/json' in resp.headers['Content-Type']
        if not resp.is_json:
            logging.error('[!] unexpected resp: is not json')
        if not resp.ok or (resp.is_json and 'errors' in resp.json()):
            raise APIError(platform='',
                           data={**resp.json(),
                                 'url': self.base_url + url,
                                 'reason': resp.reason,
                                 'errors': (resp.json().get('errors')
                                            if resp.is_json else resp.content),
                                 'status_code': resp.status_code},
                           explain=resp.reason)
        return resp

    def get(self, url: str, *args, **kwargs):
        return self._req(url, 'get', *args, **kwargs)

    def post(self, url: str, *args, **kwargs):
        return self._req(url, 'post', *args, **kwargs)

    def put(self, url: str, *args, **kwargs):
        return self._req(url, 'put', *args, **kwargs)

    def patch(self, url: str, *args, **kwargs):
        return self._req(url, 'patch', *args, **kwargs)

    def delete(self, url: str, *args, **kwargs):
        return self._req(url, 'delete', *args, **kwargs)
