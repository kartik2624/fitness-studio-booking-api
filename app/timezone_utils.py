# Small helper module dedicated to timezone handling.
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def to_ist_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    ist_dt = dt.astimezone(IST)
    return ist_dt.replace(tzinfo=None)


def attach_ist(dt: datetime) -> datetime:
   return dt.replace(tzinfo=IST)


def now_ist_naive() -> datetime:
    return datetime.now(IST).replace(tzinfo=None)
