import logging
import os
import re
from typing import Dict, Optional, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit

from errors import InvalidPlatormCampaignName


def add_token_to_uri(uri: str, token: str) -> str:
    """ add token to uri """
    parsed_url = urlparse(uri)
    if not parsed_url.query:
        uri += '?token=' + token
    elif 'token=' not in parsed_url.query:
        uri += '&token=' + token
    elif '{token}' in parsed_url.query:
        uri = uri.format(token=token)
    elif '%7Btoken%7D' in uri:  # uri-encoded {token}
        uri = uri.replace('%7Btoken%7D', token)

    return uri


def update_client_id_in_uri(uri: str, client_id: str) -> str:
    """ update client_id in uri """

    if '{client_id}' in uri:
        uri = uri.format(client_id=client_id)
    elif '%7Bclient_id%7D' in uri:  # uri-encoded {client_id}
        uri = uri.replace('%7Bclient_id%7D', client_id)

    return uri


def fix_date_interval_value(date_interval: str) -> str:
    r""" @date_interval: \d[dwmy] """
    # allowed:
    #    all
    #    thisWeek
    #    lastWeek
    #    thisMonth
    #    lastMonth
    #    lastSeven
    #    today
    #    yesterday
    #    last30Days
    return {
        '1d': 'today',
        '7d': 'lastSeven',
        '30d': 'last30Days',
    }.get(date_interval.lower(), date_interval)


def get_thrive_id_from_camp(camp: Dict[Union['id', 'name'], Union[str, int]],
                            raise_=not os.getenv('DEBUG')) -> Optional[int]:
    if not (match := re.match(r'(?P<thrive_camp_id>\d+) ', camp['name'])):
        err_msg = f"Camp {camp['id']} Named '{camp['name']}' Doesn't Contain THRIVE Camp-ID."
        if raise_:
            raise InvalidPlatormCampaignName(
                platform='MGID',
                data=err_msg)
        logging.error(f'[!] {err_msg}')
        return None
    return match.group('thrive_camp_id')
