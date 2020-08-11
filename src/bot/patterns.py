import re

from config import DEFAULT_ALL_CAMPAIGNS_ALIAS

date = r'\d\d\d\d-\d\d-\d\d'
date_interval = r'(?: ?(?P<time_interval>\d+[dwmy]))'  # 1d | 3d | 7d
date_interval_string = r'(?: ?(?P<time_interval>\w+?))'  # today | yesterday
date_interval_combined = r'(?: ?(?P<time_interval>\d{1,6}[dwmy]|[a-z]+))'
uuid4hex = r'(?:[a-f0-9]{8}(?:-?[a-f0-9]{4}){3}-?[a-f0-9]{12})'
campaign_id = rf'(?: (?P<campaign_id>(?:\d+|{uuid4hex}|{DEFAULT_ALL_CAMPAIGNS_ALIAS})(?!\w)))'
filter_limit = r'(?: (?P<filter_limit>\d+(?!\w)))'
threshold = r'(?: (?P<threshold>\d+(?:\.\d+)?(?!\w)))'
ignore_errors_keyname = 'ignore_errors'
GET_FIELDS_OPTIONS_KEYNAME = 'get_fields_options'
FIELDS_OPTIONS_FLAG = 'list-fields'
widget_id = rf'(?: (?P<widget_id>(?:{DEFAULT_ALL_CAMPAIGNS_ALIAS}|[\w-]+)(?!\w)))'


class Commands:
    LIST_CAMPAIGNS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>list)'
                                + f'{campaign_id}?',
                                re.IGNORECASE)
    # LIST_SORCES = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>sources)', re.IGNORECASE)
    CAMPAIGN_STATS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>stats)'
                                + f'{campaign_id}?'
                                + f'{date_interval_combined}?',
                                re.IGNORECASE)
    SPENT_CAMPAIGN = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>spent)'
                                + f'{campaign_id}?'
                                + f'{date_interval_combined}?',
                                re.IGNORECASE)
    BOT_TRAFFIC = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>bot-traffic)'
                             + f'{campaign_id}?'
                             + f'{date_interval_combined}?',
                             re.IGNORECASE)
    WIDGETS_STATS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>widgets-stats)'
                               + f'{campaign_id}'
                               + f'{widget_id}?'
                               + f'{filter_limit}?'
                               + f'{date_interval_combined}?',
                               re.IGNORECASE)
    WIDGETS_TOP = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>widgets-top)'
                             + f'{campaign_id}'
                             + f'{filter_limit}?'
                             + f'{date_interval_combined}?',
                             re.IGNORECASE)
    WIDGETS_HIGH_CPA = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>widgets-high-cpa)'
                                  + f'{campaign_id}'
                                  + f'{threshold}'
                                  + f'{date_interval_combined}?',
                                  re.IGNORECASE)
    WIDGETS_LOW_CPA = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>widgets-low-cpa)'
                                 + f'{campaign_id}'
                                 + f'{threshold}'
                                 + f'{date_interval_combined}?',
                                 re.IGNORECASE)
    WIDGETS_KILL_LONGTAIL = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>widgets-kill-longtail)'
                                       + f'{campaign_id}'
                                       + f'{threshold}',
                                       re.IGNORECASE)
    WIDGETS_TURN_ON_ALL = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>widgets-turn-on-all)'
                                     + f'{campaign_id}',
                                     re.IGNORECASE)
    WIDGETS_KILL_BOT_TRAFFIC = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>widgets-kill-bot|kill-bot)'
                                          + f'{campaign_id}'
                                          + f'{threshold}'
                                          + f'{date_interval_combined}',
                                          re.IGNORECASE)


class Flags:
    PREFIX_FLAG = '(?:--|/)'
    OUTPUT_FORMAT = re.compile(rf' {PREFIX_FLAG}output[: =](?P<output_format>\w+)', re.IGNORECASE)
    FILTER_FIELDS = re.compile(rf' {PREFIX_FLAG}fields[: =](?P<fields>[a-z]+(?:,[a-z]*)*)', re.IGNORECASE)
    DATE_RANGE = re.compile(rf' {PREFIX_FLAG}(?:date|date_range)[: =]'
                            + rf'(?P<date_range>{date}(?:-{date})?)', re.IGNORECASE)
    TIME_RANGE = re.compile(rf' {PREFIX_FLAG}(?:time|time_range|date_interval)[: =]'
                            + f'{date_interval_combined}', re.IGNORECASE)
    FILTER_LIMIT = re.compile(rf' {PREFIX_FLAG}limit[: =]{filter_limit}', re.IGNORECASE)
    IGNORE_ERRORS = re.compile(rf' {PREFIX_FLAG}(?P<{ignore_errors_keyname}>ie|ignore(?:[-_]errors)?)',
                               re.IGNORECASE)
    FIELDS_OPTIONS = re.compile(rf' {PREFIX_FLAG}(?P<{GET_FIELDS_OPTIONS_KEYNAME}>{FIELDS_OPTIONS_FLAG})',
                                re.IGNORECASE)


NON_BASE_DATE_INTERVAL_RE = re.compile('([2-689]|[12][0-9])d', re.IGNORECASE)
DATE_DAYS_INTERVAL_RE = re.compile(r'(\d{1,6})d', re.IGNORECASE)
