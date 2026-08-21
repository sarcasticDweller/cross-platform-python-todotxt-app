# Ensure date(/time) conversions are handled consistently across the codebase by using this helper library.
import datetime


def str_to_date(string: str) -> datetime.date | None:
    return datetime.date.fromisoformat(string) if string else None

def str_to_datetime(string: str) -> datetime.date | None:
    return datetime.datetime.fromisoformat(string) if string else None

def date_to_str(date: datetime.date | datetime.datetime) -> str:
    return date.isoformat() if date else ""

def today() -> datetime.date:
    return datetime.datetime.now().date() #noqa DTZ005: use local time
    # the real thing that should be flagged is that the annotation says this returns a date, but its actually a datetime. whether or not that's problematic is beyond me

def get_datetime(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int
) -> datetime.datetime:
    return datetime.datetime(year, month, day, hour, minute, second)  # noqa: DTZ001
    # use local time
