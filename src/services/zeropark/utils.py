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
    return {
        '1d': 'TODAY',
        '7d': 'LAST_7_DAYS',
        '30d': 'LAST_30_DAYS',
    }.get(date_interval.lower(), date_interval)
