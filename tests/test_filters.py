from __future__ import annotations

from datetime import datetime, timezone

from log_analyzer.filters import LogFilter
from log_analyzer.parser import LogEntry, parse_utc_timestamp


def make_entry(ts="2026-09-01T00:00:00Z", level="INFO", source="svc"):
    return LogEntry(parse_utc_timestamp(ts), level, source, "CODE", "msg")


def test_no_filter_matches_everything():
    f = LogFilter()
    assert f.matches(make_entry())
    assert f.matches(make_entry(level="ERROR", source="x"))


def test_level_filter():
    f = LogFilter(level="ERROR")
    assert f.matches(make_entry(level="ERROR"))
    assert not f.matches(make_entry(level="INFO"))


def test_source_filter():
    f = LogFilter(source="auth-api")
    assert f.matches(make_entry(source="auth-api"))
    assert not f.matches(make_entry(source="other"))


def test_from_ts_inclusive():
    f = LogFilter(from_ts=parse_utc_timestamp("2026-09-01T12:00:00Z"))
    assert f.matches(make_entry(ts="2026-09-01T12:00:00Z"))
    assert f.matches(make_entry(ts="2026-09-01T12:00:01Z"))
    assert not f.matches(make_entry(ts="2026-09-01T11:59:59Z"))


def test_to_ts_exclusive():
    f = LogFilter(to_ts=parse_utc_timestamp("2026-09-01T12:00:00Z"))
    assert not f.matches(make_entry(ts="2026-09-01T12:00:00Z"))
    assert f.matches(make_entry(ts="2026-09-01T11:59:59Z"))


def test_combined_filters():
    f = LogFilter(
        from_ts=parse_utc_timestamp("2026-09-01T00:00:00Z"),
        to_ts=parse_utc_timestamp("2026-09-01T12:00:00Z"),
        level="ERROR",
        source="payment-worker",
    )
    assert f.matches(make_entry(ts="2026-09-01T06:00:00Z", level="ERROR", source="payment-worker"))
    assert not f.matches(make_entry(ts="2026-09-01T06:00:00Z", level="INFO", source="payment-worker"))
    assert not f.matches(make_entry(ts="2026-09-01T12:00:00Z", level="ERROR", source="payment-worker"))
    assert not f.matches(make_entry(ts="2026-09-01T06:00:00Z", level="ERROR", source="other"))


def test_from_equals_to_empty_window():
    t = parse_utc_timestamp("2026-09-01T12:00:00Z")
    f = LogFilter(from_ts=t, to_ts=t)
    assert not f.matches(make_entry(ts="2026-09-01T12:00:00Z"))