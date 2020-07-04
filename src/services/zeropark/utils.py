from bot.patterns import NON_BASE_DATE_INTERVAL_RE
from errors import InvalidCommandFlag


def fix_date_interval_value(date_interval: str) -> str:
    r""" @date_interval: \d[dwmy] """
    # allowed:
    #   TODAY
    #   YESTERDAY
    #   LAST_7_DAYS
    #   THIS_MONTH
    #   LAST_30_DAYS
    #   LAST_MONTH
    #   THIS_QUARTER
    #   THIS_YEAR
    #   LAST_YEAR
    #   CUSTOM (using startDate and endDate query args)
    base_intervals = {
        '1d': 'TODAY',
        '7d': 'LAST_7_DAYS',
        '30d': 'LAST_30_DAYS',
    }
    if date_interval.lower() in base_intervals:
        return base_intervals[date_interval.lower()]
    if (match := NON_BASE_DATE_INTERVAL_RE.match(date_interval)):
        return 'CUSTOM'
    raise InvalidCommandFlag(flag='time_range')
