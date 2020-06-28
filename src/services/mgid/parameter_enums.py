from enum import Enum


class DateIntervalParams(str, Enum):
    all: str
    thisWeek: str
    lastWeek: str
    thisMonth: str
    lastMonth: str
    lastSeven: str
    today: str
    yesterday: str
    last30Days: str
