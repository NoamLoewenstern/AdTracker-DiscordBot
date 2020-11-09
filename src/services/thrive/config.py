from enum import Enum

SOURCE_MAPPER = {
    3: 'MGID',
    7: 'ZeroPark',
}


STATS_BY_VARIABLE_MAPPER = {
    'mgid_widgets': 'v3',
    'zeropark_widgets': 'v1',
    'by_device_type': 'type',

}


class CAMP_STATS_VARIABLE_TYPES(str, Enum):
    mgid_widgets = 'mgid_widgets'
    zeropark_widgets = 'zeropark_widgets'
    by_device_type = 'by_device_type'
