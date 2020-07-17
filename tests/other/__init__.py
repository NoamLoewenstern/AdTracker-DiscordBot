from json import dumps
from pathlib import Path


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    if 'Internal Error' in data:
        return False
    dbg_path.write_text(data)
    return True
