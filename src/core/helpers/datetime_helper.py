import time
from collections import namedtuple
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Union


def sync_first_of_month(
    dt: Union[datetime, date] = datetime.now(timezone.utc)
) -> datetime:
    return datetime(dt.year, dt.month, 1)


def sync_last_of_month(
    dt: Union[datetime, date] = datetime.now(timezone.utc)
) -> datetime:
    return datetime(dt.year, (dt.month + 1), 1) - timedelta(seconds=1)


class DateTimeHelper(object):
    @property
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def add_minutes(self, dt: datetime, minutes: int) -> datetime:
        return dt + timedelta(minutes=minutes)

    def start_of_day(self, dt: datetime) -> datetime:
        return datetime(dt.year, dt.month, dt.day)

    def tomorrow(self, dt: datetime) -> datetime:
        return datetime(dt.year, dt.month, dt.day) + timedelta(days=1)

    def n_next_day(self, n: int, dt: datetime = datetime.now(timezone.utc)) -> datetime:
        return datetime(dt.year, dt.month, dt.day) + timedelta(days=n)

    def end_of_day(self, dt: datetime) -> datetime:
        return (
            datetime(dt.year, dt.month, dt.day)
            + timedelta(days=1)
            - timedelta(seconds=1)
        )

    def yesterday(self, dt: datetime) -> datetime:
        return datetime(dt.year, dt.month, dt.day) - timedelta(days=1)

    def first_of_month(self, dt: Optional[Union[datetime, date]] = None) -> datetime:
        dt_ = dt or self.now
        return datetime(dt_.year, dt_.month, 1)

    def last_of_month(self, dt: Union[datetime, date] = None) -> datetime:
        dt_ = dt or self.now
        next_month = dt_.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        return datetime(
            last_day.year,
            last_day.month,
            last_day.day,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )

    def next_week(self, dt: Union[datetime, date] = None) -> datetime:
        dt_ = dt or self.now
        return dt_ - timedelta(days=7)

    async def get_overlapped_time(
        self,
        from_datetime_1: datetime,
        end_datetime_1: datetime,
        from_datetime_2: datetime,
        end_datetime_2: datetime,
    ) -> float:
        _range = namedtuple("Range", ["start", "end"])
        r1 = _range(start=from_datetime_1, end=end_datetime_1)
        r2 = _range(start=from_datetime_2, end=end_datetime_2)
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).seconds
        return max(0, delta)

    def get_month_name(self, month_num: int) -> str:
        return [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ][month_num - 1]

    def str_time_to_seconds(self, in_time: str) -> float:
        time_ = time.strptime(in_time, "%H:%M")
        return timedelta(
            hours=time_.tm_hour,
            minutes=time_.tm_min,
            seconds=time_.tm_sec,
        ).total_seconds()

    def last_year(self, dt: datetime = None) -> datetime:
        dt_ = dt or self.now
        return datetime(dt_.year - 1, dt_.month, dt_.day)


datetime_helper = DateTimeHelper()
