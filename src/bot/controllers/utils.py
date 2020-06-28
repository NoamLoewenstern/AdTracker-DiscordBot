import json


def convert_dict_to_raw_string(resp: list):
    raw_resp = []
    for key, value in resp.items():
        raw_resp.append(f'{key}: {value}')
    return '\n'.join(raw_resp)


def convert_resp_to_raw_string(resp):
    if isinstance(resp, str):
        # all rest-api results are json type.
        resp = json.loads(resp)
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
        return '\n'.join(raw_resp)
