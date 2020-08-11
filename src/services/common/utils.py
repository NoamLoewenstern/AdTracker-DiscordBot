import os
import re
from datetime import date, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from bot.patterns import (DATE_DAYS_INTERVAL_RE, GET_FIELDS_OPTIONS_KEYNAME,
                          NON_BASE_DATE_INTERVAL_RE)
from constants import DEBUG
from errors import CampaignNameMissingTrackerIDError, InvalidCampaignIDError
from logger import logger
from utils import AbstractDictForcedKey

from .schemas import BaseModel


class CampaignIDsDict(AbstractDictForcedKey):
    def __init__(self, d=None, /, platform: str = '', **kwargs) -> None:
        super().__init__(d, on_key_hook=str, **kwargs)
        self.platform = platform

    def __getitem__(self, key):
        try:
            return super().__getitem__(str(key))
        except KeyError:
            raise InvalidCampaignIDError(key, self.platform)


def get_thrive_id_from_camp(campaign: Dict[Literal['id', 'name'], Union[str, int]],
                            raise_=not DEBUG,
                            platform='') -> Optional[int]:
    if not (match := re.match(r'(?P<thrive_camp_id>\d+) ', campaign['name'])):
        err_msg = f"Campaign {campaign['id']} Named '{campaign['name']}' Missing Tracker ID Reference."
        if raise_:
            logger.warning(f'{err_msg}')
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


def fields_list_hook(obj: Union[List[str], Dict[str, Any], BaseModel],
                     extra_fields: List[str] = None,
                     format_result: Callable[[List[str]], Any] = lambda result: ', '.join(result),
                     ) -> Callable:
    """ Adds options to return list of field-types,
    if specific arguments passed {GET_FIELDS_OPTIONS_KEYNAME} into **kwargs """
    def extract_fields_from_obj() -> List[str]:
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict):
            return list(obj.keys())
        if isinstance(obj, type(BaseModel)):
            dynamic_properties = [key for key, value in obj.__dict__.items()
                                  if isinstance(value, property) and not key.startswith('_')]
            fields = dynamic_properties + list(obj.__fields__.keys())
            return fields

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # result from func: fix_date_interval_value
            if kwargs.get(GET_FIELDS_OPTIONS_KEYNAME):
                fields = extract_fields_from_obj()
                if extra_fields:
                    fields.extend(extra_fields)
                return format_result(fields)
            return func(*args, **kwargs)
        return wrapper
    allowed_objs_type = (list, dict, type(BaseModel))
    if not isinstance(obj, allowed_objs_type):
        raise ValueError(f'Not Excpected Type for obj of type {type(obj)}.')
    return decorator


def filter_result_by_fields(list_obj: List[Union[BaseModel, Dict[str, Any]]],
                            fields: List[str],
                            case_sensitive=False,
                            ) -> List[Dict]:
    def get_fixed_case_obj(obj) -> Dict[str, Any]:
        if case_sensitive:
            return obj
        if isinstance(obj, BaseModel):
            obj = obj.dict()
        dict_forced_lowercase_keys = AbstractDictForcedKey(obj, on_key_hook=lambda key: str(key).lower())
        return dict_forced_lowercase_keys

    if not fields:
        return list_obj
    if not case_sensitive:
        fields = [field.lower() for field in fields]
    result = []
    for obj in list_obj:
        filterd_obj = {}
        obj = get_fixed_case_obj(obj)
        for field in fields:
            try:
                filterd_obj[field] = obj[field]
            except KeyError:
                pass
        result.append(filterd_obj)
    return result
