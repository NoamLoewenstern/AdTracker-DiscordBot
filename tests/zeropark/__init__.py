from json import dumps
from pathlib import Path

PLATFORM = 'zeropark'
TEST_CAMPAING_ID = '03e0e360-9aa6-11ea-9cab-12e5dcaa70ed'


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    if 'Internal Error' in data:
        return False
    dbg_path.write_text(data)
    return True
