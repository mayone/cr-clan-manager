from datetime import datetime, timedelta, timezone

ISO8601_COMPACT_FMT = "%Y%m%dT%H%M%S.%fZ"


def get_now() -> datetime:
    return datetime.now()


def get_utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_utcnow_str(fmt: str = ISO8601_COMPACT_FMT) -> str:
    return datetime.now(timezone.utc).strftime(fmt)


def dt_to_str(dt: datetime, fmt: str = ISO8601_COMPACT_FMT) -> str:
    return dt.strftime(fmt)


def datetime_from_str(iso8601_str: str) -> datetime:
    return datetime.strptime(iso8601_str, ISO8601_COMPACT_FMT).replace(tzinfo=timezone.utc)


def utc_to_local(dt: datetime) -> datetime:
    return dt.astimezone(tz=None).replace(tzinfo=None)


def utc_shift_tz(dt: datetime, hours: int = 8) -> datetime:
    return dt.astimezone(timezone(offset=timedelta(hours=hours))).replace(tzinfo=None)


def get_date_str(dt: datetime) -> str:
    return dt.strftime("%Y%m%d")


def utc_str_to_local_date_str(iso8601_str: str) -> str:
    """Convert a UTC ISO 8601 compact string to a local date string (YYYYMMDD)."""
    return get_date_str(utc_to_local(datetime_from_str(iso8601_str)))


def get_rounded_str(tdelta: timedelta) -> str:
    if tdelta > timedelta(weeks=1):
        return f"{tdelta.days // 7} 週"
    elif tdelta > timedelta(days=1):
        return f"{tdelta.days} 天"
    elif tdelta > timedelta(hours=1):
        return f"{tdelta.seconds // 3600} 時"
    elif tdelta > timedelta(minutes=1):
        return f"{tdelta.seconds // 60} 分"
    else:
        return f"{tdelta.seconds} 秒"
