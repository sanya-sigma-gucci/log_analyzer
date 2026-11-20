from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .analyzer import analyze_file
from .filters import LogFilter
from .output import print_summary, save_report
from .parser import VALID_LEVELS, parse_utc_timestamp


def _parse_utc_arg(s: str):
    try:
        return parse_utc_timestamp(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def _parse_level_arg(s: str) -> str:
    if s not in VALID_LEVELS:
        raise argparse.ArgumentTypeError(
            f"invalid level {s!r}; expected one of {sorted(VALID_LEVELS)}"
        )
    return s


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="log_analyzer",
        description="Streaming CLI analyzer for large event logs.",
    )
    p.add_argument("-i", "--input", required=True, help="Path to the log file (required).")
    p.add_argument(
        "--from", dest="from_ts", type=_parse_utc_arg, default=None,
        help="Start timestamp (inclusive), ISO 8601 UTC (e.g. 2026-09-01T00:00:00Z).",
    )
    p.add_argument(
        "--to", dest="to_ts", type=_parse_utc_arg, default=None,
        help="End timestamp (exclusive), ISO 8601 UTC.",
    )
    p.add_argument(
        "--level", type=_parse_level_arg, default=None,
        help="Filter by level: TRACE, DEBUG, INFO, WARN, ERROR.",
    )
    p.add_argument("--source", default=None, help="Filter by source (exact match).")
    p.add_argument(
        "-n", "--top", type=int, default=10,
        help="Top-N error codes (0 = show all). Default: 10.",
    )
    p.add_argument(
        "--format", choices=["json", "csv"], default="json",
        help="Report file format (default: json).",
    )
    p.add_argument(
        "-o", "--output", default=None,
        help="Path to the report file. If omitted, no file is written.",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.top < 0:
        parser.error("--top must be >= 0")

    log_filter = LogFilter(
        from_ts=args.from_ts,
        to_ts=args.to_ts,
        level=args.level,
        source=args.source,
    )

    try:
        summary = analyze_file(args.input, log_filter, top_n=args.top)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"Error: cannot read input file {args.input!r}: {e}", file=sys.stderr)
        return 2

    print_summary(summary, args.input, sys.stdout)

    if args.output:
        try:
            save_report(summary, args.input, args.output, args.format)
        except OSError as e:
            print(f"Error: cannot write output file: {e}", file=sys.stderr)
            return 3
        print(f"\nReport saved to: {args.output} ({args.format})", file=sys.stdout)

    return 0


if __name__ == "__main__":
    sys.exit(main())