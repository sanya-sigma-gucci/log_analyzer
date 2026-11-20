from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional


VALID_LEVELS = frozenset({"TRACE", "DEBUG", "INFO", "WARN", "ERROR"})


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    source: str
    event_code: str
    message: str


@dataclass(frozen=True)
class ParseError:
    line_number: int
    raw_line: str
    reason: str


def parse_utc_timestamp(s: str) -> datetime:
    """Parse an ISO-8601 UTC timestamp. Accepts Z / +00:00 / -00:00 offsets.

    Raises ValueError for missing timezone or non-zero offset.
    """
    normalized = s[:-1] + "+00:00" if s.endswith("Z") else s
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as e:
        raise ValueError(f"invalid timestamp {s!r}: {e}") from e
    if dt.tzinfo is None:
        raise ValueError(f"timestamp must include UTC offset (e.g. 'Z'): {s!r}")
    if dt.utcoffset() != timedelta(0):
        raise ValueError(f"timestamp must be UTC (offset 0): {s!r}")
    return dt.astimezone(timezone.utc)


def parse_line(
    line_number: int, raw_line: str
) -> tuple[Optional[LogEntry], Optional[ParseError]]:
    """Parse one log line. Returns (entry, error) — exactly one is not None."""
    line = raw_line.rstrip("\r\n")

    if not line.strip():
        return None, ParseError(line_number, line, "empty line")

    parts = line.split("|")
    if len(parts) != 5:
        return None, ParseError(
            line_number,
            line,
            f"expected 5 fields separated by '|', got {len(parts)}",
        )

    ts_str, level_str, source_str, code_str, msg_str = (p.strip() for p in parts)

    if not ts_str:
        return None, ParseError(line_number, line, "empty 'timestamp' field")
    if not level_str:
        return None, ParseError(line_number, line, "empty 'level' field")
    if not source_str:
        return None, ParseError(line_number, line, "empty 'source' field")
    if not code_str:
        return None, ParseError(line_number, line, "empty 'eventCode' field")
    if not msg_str:
        return None, ParseError(line_number, line, "empty 'message' field")

    if level_str not in VALID_LEVELS:
        return None, ParseError(
            line_number,
            line,
            f"invalid level {level_str!r}; expected one of {sorted(VALID_LEVELS)}",
        )

    try:
        ts = parse_utc_timestamp(ts_str)
    except ValueError as e:
        return None, ParseError(line_number, line, str(e))

    return LogEntry(ts, level_str, source_str, code_str, msg_str), None