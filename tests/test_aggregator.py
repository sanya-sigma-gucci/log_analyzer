from __future__ import annotations

from log_analyzer.aggregator import Summary
from log_analyzer.parser import ParseError


def test_summary_defaults():
    s = Summary()
    assert (s.total_lines, s.valid_lines, s.invalid_lines, s.filtered_events) == (0, 0, 0, 0)
    assert s.by_level == {} and s.by_source == {} and s.top_error_codes == {}
    assert s.errors == []


def test_finalize_sorts_dicts():
    s = Summary()
    s.by_level = {"WARN": 2, "ERROR": 1, "INFO": 5}
    s.by_source = {"z": 1, "a": 2}
    s.top_error_codes = {"B": 1, "A": 1, "C": 3}
    s.errors = [ParseError(3, "x", "r3"), ParseError(1, "y", "r1"), ParseError(2, "z", "r2")]
    s.finalize(top_n=10)
    assert list(s.by_level.items()) == [("ERROR", 1), ("INFO", 5), ("WARN", 2)]
    assert list(s.by_source.items()) == [("a", 2), ("z", 1)]
    assert list(s.top_error_codes.items()) == [("C", 3), ("A", 1), ("B", 1)]
    assert [e.line_number for e in s.errors] == [1, 2, 3]


def test_finalize_top_n_limit():
    s = Summary()
    s.top_error_codes = {f"CODE{i}": i for i in range(1, 6)}
    s.finalize(top_n=3)
    assert len(s.top_error_codes) == 3
    assert list(s.top_error_codes.keys()) == ["CODE5", "CODE4", "CODE3"]


def test_finalize_top_n_zero_means_all():
    s = Summary()
    s.top_error_codes = {f"CODE{i}": i for i in range(1, 6)}
    s.finalize(top_n=0)
    assert len(s.top_error_codes) == 5