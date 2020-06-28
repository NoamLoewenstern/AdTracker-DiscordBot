import re

date = r'\d\d\d\d-\d\d-\d\d'
date_interval = r'(?: (?P<time_interval>\d[dwmy]))'  # 1d | 3d | 7d
date_interval_string = r'(?: (?P<time_interval>\w+?))'  # today | yesterday
date_interval_combined = rf'(?: (?P<time_interval>(\d[a-z]|\w+)))'

LIST_CAMPAIGNS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>camps|list)', re.IGNORECASE)
LIST_SORCES = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>sources)', re.IGNORECASE)
CAMPAIGN_STATS = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>stats) (?P<campaign_id>\d+)'
                            + fr'{date_interval_combined}?',
                            re.IGNORECASE)
BOT_TRAFFIC = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>bot-traffic) (?P<campaign_id>\d+)'
                         + fr'{date_interval_combined}?',
                         re.IGNORECASE)
SPENT_CAMPAIGN = re.compile(r'^/(?P<platform>\w+?) (?P<cmd>spent) (?P<campaign_id>\d+)'
                            + fr'{date_interval_combined}?',
                            re.IGNORECASE)
OUTPUT_FORMAT = re.compile(r'/output:(?P<output_format>\w+)', re.IGNORECASE)
FILTER_FIELDS = re.compile(r'/fields:(?P<fields>[a-z]+(?:,[a-z]*)*)', re.IGNORECASE)
DATE_RANGE = re.compile(rf'/range:(?P<date_range>{date}(?:-{date})?)', re.IGNORECASE)
