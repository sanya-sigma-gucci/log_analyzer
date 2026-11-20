from __future__ import annotations

from datetime import datetime, timezone

import pytest

from log_analyzer.analyzer import analyze_file, analyze_stream
from log_analyzer.filters import LogFilter


def _lines():
    return [
        "2026-09-01T00:08:59Z | WARN | auth-api | AUTH_LOGIN_OK | User session created\n",
        "2026-09-01T00:20:18Z | ERROR | payment-worker | PAYMENT_TIMEOUT | Payment provider timed out\n",
        "bad line without pipes\n",
        "2026-09-01T00:47:04Z | INFO | auth-api | AUTH_TOKEN_EXPIRED | Access token expired\n",
        "2026-09-01T00:50:00Z | ERROR | payment-worker | PAYMENT_TIMEOUT | Another timeout\n",
        "\n",
    ]


def test_analyze_stream_basic():
    s = analyze_stream(_lines(), LogFilter())
    assert s.total_lines == 6
    assert s.valid_lines == 4
    assert s.invalid_lines == 2
    assert s.filtered_events == 4
    assert s.by_level == {"ERROR": 2, "INFO": 1, "WARN": 1}
    assert s.by_source == {"auth-api": 2, "payment-worker": 2}
    assert s.top_error_codes == {"PAYMENT_TIMEOUT": 2}
    assert [e.line_number for e in s.errors] == [3, 6]


def test_analyze_stream_with_filter():
    s = analyze_stream(_lines(), LogFilter(level="ERROR"))
    assert s.filtered_events == 2
    assert s.by_level == {"ERROR": 2}


def test_analyze_stream_from_to():
    s = analyze_stream(
        _lines(),
        LogFilter(
            from_ts=datetime(2026, 9, 1, 0, 20, 0, tzinfo=timezone.utc),
            to_ts=datetime(2026, 9, 1, 0, 50, 0, tzinfo=timezone.utc),
        ),
    )
    assert s.filtered_events == 2


def test_analyze_stream_empty():
    s = analyze_stream([], LogFilter())
    assert s.total_lines == 0 and s.filtered_events == 0


def test_analyze_stream_only_errors():
    s = analyze_stream(["bad\n", "also bad\n"], LogFilter())
    assert s.total_lines == 2
    assert s.valid_lines == 0
    assert s.invalid_lines == 2
    assert s.by_level == {}


def test_analyze_stream_top_n():
    lines = [f"2026-09-01T00:00:0{i}Z | ERROR | svc | CODE_{i} | msg\n" for i in range(5)]
    s = analyze_stream(lines, LogFilter(), top_n=2)
    assert len(s.top_error_codes) == 2


def test_analyze_file(tmp_path):
    p = tmp_path / "log.txt"
    p.write_text("".join(_lines()), encoding="utf-8")
    s = analyze_file(str(p), LogFilter())
    assert s.total_lines == 6 and s.filtered_events == 4


def test_analyze_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze_file(str(tmp_path / "missing.log"), LogFilter())


def test_analyze_file_empty(tmp_path):
    p = tmp_path / "empty.log"
    p.write_text("", encoding="utf-8")
    s = analyze_file(str(p), LogFilter())
    assert s.total_lines == 0 and s.valid_lines == 0


def test_analyze_large_file(tmp_path):
    p = tmp_path / "big.log"
    with open(p, "w", encoding="utf-8") as f:
        for i in range(5000):
            f.write(f"2026-09-01T00:00:{i % 60:02d}Z | INFO | svc{i % 3} | CODE | msg\n")
    s = analyze_file(str(p), LogFilter())
    assert s.total_lines == 5000
    assert s.valid_lines == 5000