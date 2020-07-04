
from typing import Dict, Optional, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit

from bot.patterns import NON_BASE_DATE_INTERVAL_RE
from errors import InvalidCommandFlag


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
    #    interval
    #    all
    #    thisWeek
    #    lastWeek
    #    thisMonth
    #    lastMonth
    #    lastSeven
    #    today
    #    yesterday
    #    last30Days
    base_intervals = {
        '1d': 'today',
        '7d': 'lastSeven',
        '30d': 'last30Days',
    }
    if date_interval.lower() in base_intervals:
        return base_intervals[date_interval.lower()]
    if (match := NON_BASE_DATE_INTERVAL_RE.match(date_interval)):
        return 'interval'
    raise InvalidCommandFlag(flag='time_range')
