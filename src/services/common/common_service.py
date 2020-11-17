import json
import re
from enum import Enum
from typing import Callable, List, Literal, Optional, Union

import requests
from constants import DEFAULT_TIMEOUT_API_REQUEST
from errors import APIError
from errors.network import AuthError
from logger import logger


class TargetType(str, Enum):
    DESKTOP = 'DESKTOP'
    DESK = 'DESK'
    MOB = 'MOB'
    MOBILE = 'MOBILE'
    BOTH = 'BOTH'


def get_target_type_by_name(name: str) -> TargetType:
    is_desktop = bool(
        re.search(f'(?<!\\w)({TargetType.DESK}|{TargetType.DESKTOP})(?!\\w)', name, re.IGNORECASE))
    is_mobile = bool(re.search(f'(?<!\\w)({TargetType.MOB}|{TargetType.MOBILE})(?!\\w)', name, re.IGNORECASE))
    if not (is_desktop ^ is_mobile):  # either both true or both false
        return TargetType.BOTH.value
    elif is_desktop:
        return TargetType.DESKTOP.value
    elif is_mobile:
        return TargetType.MOBILE.value


def error_in_keys(d: dict) -> Optional[str]:
    d_keys = [key.lower() for key in d.keys()]
    error_keys = ['error', 'errors']
    for err_key in error_keys:
        if err_key in d_keys:
            return err_key
    return None


class CommonService:
    def __init__(self, base_url: str, url_hooks: Optional[List[Callable[[str], str]]] = None):
        self.base_url = base_url
        self.session = self.__init_session()
        self.url_hooks = url_hooks if url_hooks else []

    def __init_session(self):
        session = requests.Session()
        session.headers.update({'Accept': 'application/json'})
        return session

    def _validate_resp(self, resp: requests.models.Response):
        if not resp.is_json:
            logger.error('[!] unexpected resp: is not json')
        # or (resp.is_json and 'errors' in resp.json_content):
        if not resp.ok:
            if resp.status_code == 403 or resp.json_content and 'NOT LOGGED IN' in json.dumps(resp.json_content).upper():
                reason = 'NOT LOGGED IN - Check API-KEYS'
            else:
                reason = resp.reason
            raise APIError(platform='',
                           data={**(resp.json_content if resp.is_json else {}),
                                 #  'url': self.base_url + url,
                                 'reason': reason,
                                 'error': (resp.json_content.get('error', resp.json_content.get('errors', ''))
                                           if resp.is_json else resp.content.decode()),
                                 'status_code': resp.status_code},
                           explain=resp.reason)
        if resp.ok and (resp.is_json and (err_key := error_in_keys(resp.json_content))):
            logger.error(f'[!] resp is ok, but "{err_key}" in response: {resp.json_content["errors"]}')
            raise APIError(platform='', message=f"'{err_key}' in Response", data={
                'resp_content': resp.json_content,
            })

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
        resp.json_content = resp.json() if resp.is_json else {}
        self._validate_resp(resp)
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
