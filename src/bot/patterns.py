import re

date = r'\d\d\d\d-\d\d-\d\d'
date_interval = r'(?: ?(?P<time_interval>\d+[dwmy]))'  # 1d | 3d | 7d
date_interval_string = r'(?: ?(?P<time_interval>\w+?))'  # today | yesterday
date_interval_combined = r'(?: ?(?P<time_interval>\d{1,3}[dwmy]|[a-z]+))'
uuid4hex = r'(?:[a-f0-9]{8}(?:-?[a-f0-9]{4}){3}-?[a-f0-9]{12})'
campaign_id = rf'(?: (?P<campaign_id>(?:\d|{uuid4hex})+(?!\w)))'
filter_limit = r'(?: (?P<filter_limit>\d+(?!\w)))'

LIST_CAMPAIGNS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>camps|list)'
                            + fr'{campaign_id}?',
                            re.IGNORECASE)
LIST_SORCES = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>sources)', re.IGNORECASE)
CAMPAIGN_STATS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>stats)'
                            + fr'{campaign_id}?'
                            + fr'{date_interval_combined}?',
                            re.IGNORECASE)
SPENT_CAMPAIGN = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>spent)'
                            + fr'{campaign_id}?'
                            + fr'{date_interval_combined}?',
                            re.IGNORECASE)
BOT_TRAFFIC = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>bot-traffic)'
                         + fr'{campaign_id}?'
                         + fr'{date_interval_combined}?',
                         re.IGNORECASE)
TOP_WIDGETS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>top-widgets)'
                         + fr'{campaign_id}'
                         + fr'{filter_limit}?'
                         + fr'{date_interval_combined}?',
                         re.IGNORECASE)

OUTPUT_FORMAT = re.compile(r' /output(?:[: ])(?P<output_format>\w+)', re.IGNORECASE)
FILTER_FIELDS = re.compile(r' /fields(?:[: ])(?P<fields>[a-z]+(?:,[a-z]*)*)', re.IGNORECASE)
DATE_RANGE_FLAG = re.compile(rf' /(?:date|date_range)(?:[: ])'
                             + rf'(?P<date_range>{date}(?:-{date})?)', re.IGNORECASE)
TIME_RANGE_FLAG = re.compile(rf' /(?:time|time_range|date_interval)(?:[: ])'
                             + f'{date_interval_combined}', re.IGNORECASE)

NON_BASE_DATE_INTERVAL_RE = re.compile('([2-689]|[12][0-9])d', re.IGNORECASE)
DATE_DAYS_INTERVAL_RE = re.compile('(\d{1,3})d', re.IGNORECASE)
