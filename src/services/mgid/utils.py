
from typing import Dict, Optional, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit

from bot.patterns import DATE_DAYS_INTERVAL_RE, NON_BASE_DATE_INTERVAL_RE
from errors import InvalidCommandFlag


def add_token_to_url(url: str, token: str) -> str:
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


def update_client_id_in_url(url: str, client_id: str) -> str:
    """ update client_id in url """

    if '{client_id}' in url:
        url = url.format(client_id=client_id)
    elif '%7Bclient_id%7D' in url:  # url-encoded {client_id}
        url = url.replace('%7Bclient_id%7D', client_id)

    return url


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
    if (match := DATE_DAYS_INTERVAL_RE.match(date_interval)):
        return 'interval'
    raise InvalidCommandFlag(flag='time_range')
