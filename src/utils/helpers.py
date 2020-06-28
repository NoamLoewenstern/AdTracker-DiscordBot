from functools import wraps
from typing import Callable


def alias_param(alias: str, key: str,
                callback: Callable[[str], str] = lambda value: value):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # adding alias key in arguments
            kwargs[alias] = callback(kwargs.get(key))
            return func(*args, **kwargs)
        return wrapper
    return decorator
