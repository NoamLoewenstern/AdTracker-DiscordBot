import csv
import re
import tempfile
from functools import reduce, wraps
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union

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


def merge_objs(*list_dicts: List[Dict], merge_types: Tuple[type] = (int, float)) -> dict:
    """ MERGED 2 dictionaries with the (int, float) types only.
    Every other Value Type will be OVERRIDDEN with the value from the SECOND DICT."""
    def concat_values_by_key(key, *dicts):
        def concat(val1, val2): return val1 + val2
        all_values = list(d[key] for d in dicts)
        return reduce(concat, all_values)

    common_keys = reduce(lambda d1, d2: set(d1) & set(d2), list_dicts)

    combined = {
        # merge objects' *content*, if have the same key and are of type 'merge_types'
        key: concat_values_by_key(key, *list_dicts)
        for key in common_keys
        if isinstance(list_dicts[0][key], merge_types)
    }

    merged_obj = {
        **reduce(lambda d1, d2: {**d1, **d2}, list_dicts),
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
