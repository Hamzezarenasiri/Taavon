from enum import Enum


class TimeRangeEnum(str, Enum):
    last_three_months: str = "Last three months"
    last_month: str = "Last month"
    last_week: str = "Last week"
    last_day: str = "Last day"


ALL_TIME_RANGE = [i.value for i in TimeRangeEnum.__members__.values()]
