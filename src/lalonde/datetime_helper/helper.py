import datetime


def str_to_date(string: str) -> datetime.date | None:
    return datetime.date.fromisoformat(string) if string else None

def date_to_str(date: datetime.date) -> str:
    return date.isoformat() if date else ""

def today() -> datetime.date:
    return datetime.datetime.now().date() #noqa DTZ005: use local time
