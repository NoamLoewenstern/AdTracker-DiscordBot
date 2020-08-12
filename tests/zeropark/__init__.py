from json import dumps
from pathlib import Path

PLATFORM = 'zeropark'
TEST_CAMPAING_ID = '03e0e360-9aa6-11ea-9cab-12e5dcaa70ed'


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    dbg_path.write_text(data)
    if 'Internal Error' in data or ('error' in data.lower() and 'status_code' in data.lower()) \
            or data.startswith('ERRORS'):
        return False
    return True
