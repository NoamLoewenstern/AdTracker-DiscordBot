from json import dumps
from pathlib import Path

TEST_CAMPAING_ID = 1073503
TEST_CAMPAING_ID = 1071615
TEST_DATE = '2020-05-28'
PLATFORM = 'mgid'


def log_resp(data, test_name):
    dbg_path = Path(__file__).parent / 'responses' / test_name
    data = data if isinstance(data, str) else dumps(data)
    if 'Internal Error' in data:
        return False
    dbg_path.write_text(data)
    return True
