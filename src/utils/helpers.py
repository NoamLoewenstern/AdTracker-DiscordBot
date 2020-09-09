import csv
import re
import tempfile
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Union

GENERAL_RESP_TYPE = Union[str, List[Dict[Union[str, int], Union[str, int, float, bool]]]]

OPERATORS_MAP = {
    'eq': '__eq__',
    'ne': '__ne__',
    'lt': '__lt__',
    'gt': '__gt__',
    'le': '__le__',
    'ge': '__ge__',
}

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


def chunks(lst: Iterable, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def merge_objs(obj1: Dict[str, Dict], obj2: Dict[str, Dict]) -> List[Dict]:
    """ MERGED 2 dictionaries with the (int, float) types only.
    Every other Value Type will be OVERRIDDEN with the value from the SECOND DICT."""
    common_keys = set(obj1) & set(obj2)

    combined = {
        # merge object's content if have the same key.
        key: obj1[key] + obj2[key]
        for key in common_keys
        if isinstance(obj1[key], (int, float))
    }

    merged_obj = {
        **obj1,
        **obj2,
        **combined,
    }
    return merged_obj


def groupify_list_strings(list_strings: List[str], /, size: int = 70, joiner='\n'):
    cur_iter_text = ''
    for block in list_strings:
        if len(cur_iter_text) + len(block) > size:
            yield cur_iter_text.strip(joiner)
            cur_iter_text = ''
        cur_iter_text += joiner + block
    if cur_iter_text:
        yield cur_iter_text


def is_valid_uuid4(string: str):
    return bool(re.match(r'\w{8}(-\w{4}){3}-\w{12}', string, re.IGNORECASE))


def convert_list_dicts_to_csv_file(list_dicts: GENERAL_RESP_TYPE) -> Path:
    assert list_dicts and isinstance(list_dicts, list) and list_dicts[0] and isinstance(
        list_dicts[0], dict), 'Invalid list_dicts Type.'
    keys = list(set([key for obj in list_dicts for key in obj]))
    with tempfile.NamedTemporaryFile('w', encoding='utf8', suffix='.csv', delete=False, newline='') as output_file:
        fc = csv.DictWriter(output_file,
                            fieldnames=keys,
                            )
        fc.writeheader()
        fc.writerows(list_dicts)
    return Path(output_file.name)


def format_float(num: Union[str, int, float]):
    return float(f'{num:0>5.2f}')
