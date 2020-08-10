import os
import re
from datetime import date, timedelta
from functools import wraps
from typing import Dict, Optional, Union

from bot.patterns import DATE_DAYS_INTERVAL_RE, NON_BASE_DATE_INTERVAL_RE
from constants import DEBUG
from errors import CampaignNameMissingTrackerIDError
from logger import logger


def get_thrive_id_from_camp(campaign: Dict[Union['id', 'name'], Union[str, int]],
                            raise_=not DEBUG,
                            platform='') -> Optional[int]:
    if not (match := re.match(r'(?P<thrive_camp_id>\d+) ', campaign['name'])):
        err_msg = f"Campaign {campaign['id']} Named '{campaign['name']}' Missing Tracker ID Reference."
        logger.error(f'{err_msg}')
        if raise_:
            raise CampaignNameMissingTrackerIDError(
                id=campaign['id'],
                name=campaign['name'],
                platform=platform,
            )
        return None
    return match.group('thrive_camp_id')


# decorator
def add_interval_startend_dates(converted_date_interval,
                                original_time_interval='time_interval',
                                start_date_param='startDate',
                                end_date_param='endDate',
                                custom_date_key='interval',
                                strftime=r'%Y-%m-%d',
                                ):
    """ CHECKING if the interval is "CUSTOM" for range-dates.
    is yes: then calculate the dates by the interval
    example:
        if interval is "3d" ->
        then calculates the dates from today, back 3 days, into format of  {strftime}

    Keyword arguments:
    custom_date_key -- the content that "says" that is using date-range
                            instead of range-interval.
    start_date_param -- name of argument to the startDate parameter.
    end_date_param -- name of argument to the endDate parameter.
    Return: Decorator for methods using time_interval
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """  Adding 'startDate' 'endDate' to kwargs, by dateInterval """
            # result from func: fix_date_interval_value
            if kwargs.get(converted_date_interval) != custom_date_key:
                kwargs.update({
                    start_date_param: None,
                    end_date_param: None,
                })
            else:
                match = DATE_DAYS_INTERVAL_RE.match(kwargs[original_time_interval])
                days_back = int(match.groups()[0])

                today = date.today()
                from_date = today - timedelta(days=days_back - 1)
                startDate = from_date.strftime(strftime)
                endDate = today.strftime(strftime)

                kwargs.update({
                    start_date_param: startDate,
                    end_date_param: endDate,
                })

            return func(*args, **kwargs)
        return wrapper
    return decorator
