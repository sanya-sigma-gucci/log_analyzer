from __future__ import annotations

from typing import Iterable

from .aggregator import Summary
from .filters import LogFilter
from .parser import parse_line


def analyze_stream(
    lines: Iterable[str], log_filter: LogFilter, top_n: int = 10
) -> Summary:
    """Analyze an iterable of lines without keeping them in memory."""
    summary = Summary()
    for line_number, raw_line in enumerate(lines, start=1):
        summary.total_lines += 1
        entry, error = parse_line(line_number, raw_line)
        if error is not None:
            summary.invalid_lines += 1
            summary.errors.append(error)
            continue
        summary.valid_lines += 1
        if not log_filter.matches(entry):
            continue
        summary.filtered_events += 1
        summary.by_level[entry.level] = summary.by_level.get(entry.level, 0) + 1
        summary.by_source[entry.source] = summary.by_source.get(entry.source, 0) + 1
        if entry.level == "ERROR":
            summary.top_error_codes[entry.event_code] = (
                summary.top_error_codes.get(entry.event_code, 0) + 1
            )
    summary.finalize(top_n)
    return summary


def analyze_file(path: str, log_filter: LogFilter, top_n: int = 10) -> Summary:
    """Analyze a log file. Raises FileNotFoundError / OSError if not readable."""
    with open(path, "r", encoding="utf-8") as f:
        return analyze_stream(f, log_filter, top_n)