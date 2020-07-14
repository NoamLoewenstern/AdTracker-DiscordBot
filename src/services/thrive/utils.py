import logging
import re
from typing import Dict, List, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit

from bot.patterns import DATE_DAYS_INTERVAL_RE, NON_BASE_DATE_INTERVAL_RE
from errors import InvalidCommandFlag
from utils import merged_objs

PATTERN_GET_UID = re.compile(r'^(?P<uid>\d+)s?(?P<subid>\d+)?$', re.IGNORECASE)


def add_token_to_uri(url: str, token: str) -> str:
    """ add token to url """
    parsed_url = urlparse(url)
    if not parsed_url.query:
        url += '?token=' + token
    elif 'token=' not in parsed_url.query:
        url += '&token=' + token
    elif '{token}' in parsed_url.query:
        url = url.format(token=token)
    elif '%7Btoken%7D' in url:  # url-encoded {token}
        url = url.replace('%7Btoken%7D', token)

    return url


def update_client_id_in_uri(url: str, client_id: str) -> str:
    """ update client_id in url """

    if '{client_id}' in url:
        url = url.format(client_id=client_id)
    elif '%7Bclient_id%7D' in url:  # url-encoded {client_id}
        url = url.replace('%7Bclient_id%7D', client_id)

    return url


def fix_date_interval_value(date_interval: str) -> str:
    r""" @date_interval: \d[dwmy] """
    base_intervals = {
        '1d': 'interval',  # 'Today',
        '7d': 'interval',
        '30d': 'interval',
    }
    if date_interval.lower() in base_intervals:
        return base_intervals[date_interval.lower()]
    if (match := DATE_DAYS_INTERVAL_RE.match(date_interval)):
        return 'interval'
    raise InvalidCommandFlag(flag='time_range')


def subids_to_uids(list_objects: List[Dict['id', str]]) -> List[Dict['id', str]]:
    dict_objects = {obj['id']: obj for obj in list_objects}
    new_objects = {}
    for _id, obj in dict_objects.items():
        match = PATTERN_GET_UID.match(_id)
        if match is None:
            logging.warning(f"[subids_to_uids] Not Expected! id is not UID format. id: {_id}")
            continue
        uid = match.group('uid')
        subid = match.group('subid')
        if subid is not None:
            obj['id'] = uid
        if uid not in new_objects:
            new_objects[uid] = obj
        else:
            new_objects[uid] = merged_objs(new_objects[uid], obj)
    return list(new_objects.values())
