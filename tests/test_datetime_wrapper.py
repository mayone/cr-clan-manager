from datetime import datetime, timedelta, timezone

from utils.datetime_wrapper import (
    datetime_from_str,
    dt_to_str,
    get_date_str,
    get_now,
    get_rounded_str,
    get_utcnow,
    utc_to_local,
)


class TestGetNow:
    def test_returns_datetime(self):
        result = get_now()
        assert isinstance(result, datetime)


class TestGetUtcnow:
    def test_returns_utc_datetime(self):
        result = get_utcnow()
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc


class TestDatetimeFromStr:
    """Equivalence classes: valid ISO 8601 compact, invalid format."""

    def test_valid_iso_string(self):
        result = datetime_from_str("20230615T120000.000000Z")
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 12
        assert result.tzinfo == timezone.utc

    def test_roundtrip(self):
        original = datetime(2023, 1, 15, 8, 30, 0, tzinfo=timezone.utc)
        s = dt_to_str(original)
        restored = datetime_from_str(s)
        assert original == restored


class TestDtToStr:
    def test_formats_correctly(self):
        dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = dt_to_str(dt)
        assert result == "20230615T120000.000000Z"

    def test_custom_format(self):
        dt = datetime(2023, 6, 15)
        result = dt_to_str(dt, "%Y-%m-%d")
        assert result == "2023-06-15"


class TestUtcToLocal:
    def test_converts_to_local(self):
        utc_dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        local_dt = utc_to_local(utc_dt)
        assert local_dt.tzinfo is None
        assert isinstance(local_dt, datetime)


class TestGetDateStr:
    def test_formats_date(self):
        dt = datetime(2023, 6, 15)
        assert get_date_str(dt) == "20230615"

    def test_single_digit_month(self):
        dt = datetime(2023, 1, 5)
        assert get_date_str(dt) == "20230105"


class TestGetRoundedStr:
    """Equivalence classes: weeks, days, hours, minutes, seconds."""

    def test_weeks(self):
        result = get_rounded_str(timedelta(weeks=2, days=1))
        assert result == "2 週"

    def test_days(self):
        result = get_rounded_str(timedelta(days=3))
        assert result == "3 天"

    def test_hours(self):
        result = get_rounded_str(timedelta(hours=5))
        assert result == "5 時"

    def test_minutes(self):
        result = get_rounded_str(timedelta(minutes=30))
        assert result == "30 分"

    def test_seconds(self):
        result = get_rounded_str(timedelta(seconds=45))
        assert result == "45 秒"

    def test_boundary_exactly_one_day(self):
        result = get_rounded_str(timedelta(days=1, seconds=1))
        assert result == "1 天"
