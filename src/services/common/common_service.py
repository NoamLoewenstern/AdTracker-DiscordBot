import json
from enum import Enum
from typing import Callable, List, Literal, Optional, Union

import requests

from constants import DEFAULT_TIMEOUT_API_REQUEST
from errors import APIError
from errors.network import AuthError
from logger import logger


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
             method: Literal['get', 'post', 'put', 'patch', 'delete'],
             *args: list,
             **kwargs: dict):
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT_API_REQUEST)
        for url_hook in self.url_hooks:
            url = url_hook(url)
        logger.info(f"[REQ] [{method.upper()}] "
                    f"{self.base_url + url[:200] + '...' if len(url) > 200 else ''} ")
        resp = getattr(self.session, method)(self.base_url + url, *args, **kwargs)
        resp.is_json = 'application/json' in resp.headers['Content-Type']
        resp.json_content = resp.json() if resp.is_json else None
        if not resp.is_json:
            logger.error('[!] unexpected resp: is not json')
        if resp.ok and (resp.is_json and 'errors' in resp.json_content):
            logger.error(f'[!] resp is ok, but "Errors" in response: {resp.json_content["errors"]}')
        # or (resp.is_json and 'errors' in resp.json_content):
        if not resp.ok:
            raise APIError(platform='',
                           data={**(resp.json_content if resp.is_json else {}),
                                 #  'url': self.base_url + url,
                                 'reason': resp.reason,
                                 'error': (resp.json_content.get('error', '')
                                           if resp.is_json else resp.content),
                                 'status_code': resp.status_code},
                           explain=resp.reason)
        if resp.status_code == 403 or resp.json_content and 'NOT LOGGED IN' in json.dumps(resp.json_content).upper():
            raise AuthError(platform='',
                            data={**(resp.json_content if resp.is_json else {}),
                                  #  'url': self.base_url + url,
                                  'reason': "NOT LOGGED IN - Check API-KEYS",
                                  'error': (resp.json_content.get('error', '')
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
