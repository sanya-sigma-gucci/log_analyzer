from __future__ import annotations

import csv
import json
from typing import IO

from .aggregator import Summary


MAX_ERRORS_IN_TERMINAL = 50


def summary_to_dict(summary: Summary, input_file: str) -> dict:
    return {
        "input_file": input_file,
        "overall": {
            "total_lines": summary.total_lines,
            "valid_lines": summary.valid_lines,
            "invalid_lines": summary.invalid_lines,
            "filtered_events": summary.filtered_events,
        },
        "by_level": dict(summary.by_level),
        "by_source": dict(summary.by_source),
        "top_error_codes": dict(summary.top_error_codes),
        "parse_errors": [
            {"line": e.line_number, "reason": e.reason, "raw": e.raw_line}
            for e in summary.errors
        ],
    }


def save_json(summary: Summary, input_file: str, path: str) -> None:
    data = summary_to_dict(summary, input_file)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def save_csv(summary: Summary, input_file: str, path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "key", "value", "detail"])
        w.writerow(["input_file", "", input_file, ""])
        w.writerow(["overall", "total_lines", summary.total_lines, ""])
        w.writerow(["overall", "valid_lines", summary.valid_lines, ""])
        w.writerow(["overall", "invalid_lines", summary.invalid_lines, ""])
        w.writerow(["overall", "filtered_events", summary.filtered_events, ""])
        for lvl, cnt in summary.by_level.items():
            w.writerow(["by_level", lvl, cnt, ""])
        for src, cnt in summary.by_source.items():
            w.writerow(["by_source", src, cnt, ""])
        for code, cnt in summary.top_error_codes.items():
            w.writerow(["top_error_codes", code, cnt, ""])
        for err in summary.errors:
            w.writerow(["parse_error", f"line {err.line_number}", err.reason, err.raw_line])


def save_report(summary: Summary, input_file: str, path: str, fmt: str) -> None:
    if fmt == "json":
        save_json(summary, input_file, path)
    elif fmt == "csv":
        save_csv(summary, input_file, path)
    else:
        raise ValueError(f"unknown format: {fmt!r}")


def print_summary(summary: Summary, input_file: str, out: IO[str]) -> None:
    print("=== Log Analysis Summary ===", file=out)
    print(f"Input file: {input_file}", file=out)
    print(file=out)
    print("Overall:", file=out)
    print(f"  Total lines:    {summary.total_lines}", file=out)
    print(f"  Valid lines:    {summary.valid_lines}", file=out)
    print(f"  Invalid lines:  {summary.invalid_lines}", file=out)
    print(f"  Filtered:       {summary.filtered_events}", file=out)
    print(file=out)
    if summary.by_level:
        print("By level:", file=out)
        for lvl, cnt in summary.by_level.items():
            print(f"  {lvl:<8} {cnt}", file=out)
        print(file=out)
    if summary.by_source:
        print("By source:", file=out)
        for src, cnt in summary.by_source.items():
            print(f"  {src:<25} {cnt}", file=out)
        print(file=out)
    if summary.top_error_codes:
        print("Top error codes (ERROR level):", file=out)
        for code, cnt in summary.top_error_codes.items():
            print(f"  {code:<25} {cnt}", file=out)
        print(file=out)
    if summary.errors:
        print(f"Parse errors ({len(summary.errors)}):", file=out)
        for err in summary.errors[:MAX_ERRORS_IN_TERMINAL]:
            print(f"  Line {err.line_number}: {err.reason}", file=out)
        if len(summary.errors) > MAX_ERRORS_IN_TERMINAL:
            remaining = len(summary.errors) - MAX_ERRORS_IN_TERMINAL
            print(f"  ... and {remaining} more (see JSON/CSV output for full list)", file=out)
        print(file=out)