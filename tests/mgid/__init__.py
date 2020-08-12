from json import dumps
from pathlib import Path

TEST_CAMPAING_ID = 1073503
TEST_CAMPAING_ID = 1071615
TEST_DATE = '2020-05-28'
PLATFORM = 'mgid'


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    dbg_path.write_text(data)
    if 'Internal Error' in data or ('error' in data.lower() and 'status_code' in data.lower()) \
            or data.startswith('ERRORS'):
        return False
    return True
