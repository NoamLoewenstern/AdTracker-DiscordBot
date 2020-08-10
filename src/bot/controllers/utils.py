import json

from errors.parsers import InvalidResponseFormatTypeError


def convert_dict_to_raw_string(resp: list):
    raw_resp = []
    special_keys = {
        'id': {
            'value': '',
            'priority': 0,
        },
        'name': {
            'value': '',
            'priority': 1,
        },
    }
    for key, value in sorted(resp.items()):
        if key in special_keys:
            special_keys[key]['value'] = value
            continue
        raw_resp.append(f'{key}: {value}')
    add_special_keys = [spec_key for spec_key in special_keys
                        if special_keys[spec_key]['value']]
    add_special_keys.sort(key=lambda key: special_keys[key]['priority'],
                          reverse=True)
    for key in add_special_keys:
        value = special_keys[key]['value']
        raw_resp.insert(0, f'{key}: {value}')
    return '\n'.join(raw_resp).strip()


def convert_resp_to_raw_string(resp):
    if isinstance(resp, str):
        # all rest-api results are json type.
        try:
            resp = json.loads(resp)
        except json.decoder.JSONDecodeError:
            return resp
    if isinstance(resp, dict):
        # converting to "key: value"
        return convert_dict_to_raw_string(resp)
    if isinstance(resp, list):
        # converting to list of: "key: value"
        raw_resp = []
        for item in resp:
            if isinstance(item, dict):
                raw_resp.append(convert_dict_to_raw_string(item))
            else:
                raw_resp.append(str(item))
        return '\n\n'.join(raw_resp).strip()
    raise InvalidResponseFormatTypeError()
