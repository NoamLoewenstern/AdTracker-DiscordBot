import logging
import os
import re
from datetime import date, timedelta
from functools import wraps
from typing import Dict, Optional, Union

from bot.patterns import NON_BASE_DATE_INTERVAL_RE
from errors import InvalidPlatormCampaignName


def get_thrive_id_from_camp(campaign: Dict[Union['id', 'name'], Union[str, int]],
                            raise_=not os.getenv('DEBUG'),
                            platform='') -> Optional[int]:
    if not (match := re.match(r'(?P<thrive_camp_id>\d+) ', campaign['name'])):
        err_msg = f"Campaign {campaign['id']} Named '{campaign['name']}' Doesn't Contain THRIVE Camp-ID."
        if raise_:
            raise InvalidPlatormCampaignName(
                platform=platform,
                data=err_msg)
        logging.error(f'[!] {err_msg}')
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
                match = NON_BASE_DATE_INTERVAL_RE.match(kwargs[original_time_interval])
                days_back = int(match.groups()[0])

                today = date.today()
                from_date = today - timedelta(days=days_back)
                startDate = from_date.strftime(strftime)
                endDate = today.strftime(strftime)

                kwargs.update({
                    start_date_param: startDate,
                    end_date_param: endDate,
                })

            return func(*args, **kwargs)
        return wrapper
    return decorator
