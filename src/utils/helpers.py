from functools import wraps
from typing import Any, Callable, Dict, List, Union

from pydantic import BaseModel


# decorator
def alias_param(alias: str, key: str,
                callback: Callable[[str], str] = lambda value: value,
                replace_exists=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # adding alias key in arguments
            if key in kwargs:
                if alias not in kwargs or (alias in kwargs and replace_exists):
                    kwargs[alias] = callback(kwargs[key])
            return func(*args, **kwargs)
        return wrapper
    return decorator


def filter_result_by_fields(result: List[Union[BaseModel, Dict[str, Any]]],
                            fields: List[str]) -> List[Dict]:
    if not fields:
        return result
    return [{field: obj[field]
             for field in fields
             if field in obj}
            for obj in result]


operator_factory = {
    'eq': '__eq__',
    'ne': '__ne__',
    'lt': '__lt__',
    'gt': '__gt__',
    'le': '__le__',
    'ge': '__ge__',
}


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
