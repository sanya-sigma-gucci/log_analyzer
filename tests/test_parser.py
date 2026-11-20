from __future__ import annotations

from datetime import datetime, timezone

import pytest

from log_analyzer.parser import (
    VALID_LEVELS,
    parse_line,
    parse_utc_timestamp,
)


def test_parse_valid_line():
    line = "2026-09-01T00:08:59Z | WARN | auth-api | AUTH_LOGIN_OK | User session created\n"
    entry, err = parse_line(1, line)
    assert err is None and entry is not None
    assert entry.timestamp == datetime(2026, 9, 1, 0, 8, 59, tzinfo=timezone.utc)
    assert entry.level == "WARN"
    assert entry.source == "auth-api"
    assert entry.event_code == "AUTH_LOGIN_OK"
    assert entry.message == "User session created"


def test_parse_line_with_whitespace():
    line = "  2026-09-01T00:08:59Z   |   INFO   |  svc  |  CODE  |  msg  \n"
    entry, err = parse_line(1, line)
    assert err is None and entry is not None
    assert entry.level == "INFO" and entry.source == "svc"


def test_parse_invalid_field_count_too_few():
    entry, err = parse_line(5, "a | b | c\n")
    assert entry is None and err is not None
    assert err.line_number == 5
    assert "expected 5 fields" in err.reason


def test_parse_invalid_field_count_too_many():
    entry, err = parse_line(7, "a | b | c | d | e | f\n")
    assert entry is None and err is not None
    assert "expected 5 fields" in err.reason


def test_parse_empty_line():
    entry, err = parse_line(3, "\n")
    assert entry is None and err is not None
    assert "empty" in err.reason.lower()


def test_parse_whitespace_only_line():
    entry, err = parse_line(4, "   \t  \n")
    assert entry is None and err is not None


def test_parse_empty_timestamp():
    _, err = parse_line(2, " | INFO | svc | CODE | msg\n")
    assert "timestamp" in err.reason


def test_parse_empty_level():
    _, err = parse_line(2, "2026-09-01T00:00:00Z |  | svc | CODE | msg\n")
    assert "level" in err.reason


def test_parse_empty_source():
    _, err = parse_line(2, "2026-09-01T00:00:00Z | INFO |  | CODE | msg\n")
    assert "source" in err.reason


def test_parse_empty_event_code():
    _, err = parse_line(2, "2026-09-01T00:00:00Z | INFO | svc |  | msg\n")
    assert "eventCode" in err.reason


def test_parse_empty_message():
    _, err = parse_line(2, "2026-09-01T00:00:00Z | INFO | svc | CODE | \n")
    assert "message" in err.reason


def test_parse_invalid_level():
    _, err = parse_line(2, "2026-09-01T00:00:00Z | FATAL | svc | CODE | msg\n")
    assert "invalid level" in err.reason


def test_parse_invalid_timestamp_format():
    _, err = parse_line(2, "not-a-timestamp | INFO | svc | CODE | msg\n")
    assert "timestamp" in err.reason.lower()


def test_parse_timestamp_without_utc_marker():
    _, err = parse_line(2, "2026-09-01T00:00:00 | INFO | svc | CODE | msg\n")
    assert "UTC" in err.reason


def test_parse_timestamp_with_nonzero_offset():
    _, err = parse_line(2, "2026-09-01T00:00:00+03:00 | INFO | svc | CODE | msg\n")
    assert "UTC" in err.reason


def test_parse_utc_timestamp_z():
    dt = parse_utc_timestamp("2026-09-01T00:08:59Z")
    assert dt == datetime(2026, 9, 1, 0, 8, 59, tzinfo=timezone.utc)


def test_parse_utc_timestamp_plus_zero():
    dt = parse_utc_timestamp("2026-09-01T00:08:59+00:00")
    assert dt == datetime(2026, 9, 1, 0, 8, 59, tzinfo=timezone.utc)


def test_parse_utc_timestamp_invalid_date():
    with pytest.raises(ValueError):
        parse_utc_timestamp("2026-13-01T00:00:00Z")


def test_parse_utc_timestamp_no_utc_suffix():
    with pytest.raises(ValueError):
        parse_utc_timestamp("2026-09-01T00:00:00")


def test_parse_crlf_line():
    entry, err = parse_line(1, "2026-09-01T00:08:59Z | WARN | auth-api | CODE | msg\r\n")
    assert err is None and entry is not None


def test_parse_line_pipe_in_message_fails():
    _, err = parse_line(1, "2026-09-01T00:00:00Z | INFO | svc | CODE | msg with | pipe\n")
    assert "expected 5 fields" in err.reason


def test_valid_levels_set():
    assert VALID_LEVELS == frozenset({"TRACE", "DEBUG", "INFO", "WARN", "ERROR"})