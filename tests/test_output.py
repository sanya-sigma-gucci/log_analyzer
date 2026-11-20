from __future__ import annotations

import csv
import json
import sys

import pytest

from log_analyzer.aggregator import Summary
from log_analyzer.output import (
    print_summary,
    save_csv,
    save_json,
    save_report,
    summary_to_dict,
)
from log_analyzer.parser import ParseError


def make_summary():
    s = Summary(
        total_lines=10,
        valid_lines=8,
        invalid_lines=2,
        filtered_events=6,
        by_level={"ERROR": 3, "INFO": 3},
        by_source={"auth-api": 4, "orders-api": 2},
        top_error_codes={"PAYMENT_TIMEOUT": 2, "AUTH_DENIED": 1},
        errors=[
            ParseError(2, "bad line 2", "expected 5 fields, got 3"),
            ParseError(7, "bad line 7", "invalid level"),
        ],
    )
    s.finalize(top_n=10)
    return s


def test_summary_to_dict():
    d = summary_to_dict(make_summary(), "logs.log")
    assert d["input_file"] == "logs.log"
    assert d["overall"]["total_lines"] == 10
    assert d["by_level"] == {"ERROR": 3, "INFO": 3}
    assert d["top_error_codes"] == {"AUTH_DENIED": 1, "PAYMENT_TIMEOUT": 2}
    assert len(d["parse_errors"]) == 2
    assert d["parse_errors"][0]["line"] == 2


def test_save_json(tmp_path):
    p = tmp_path / "r.json"
    save_json(make_summary(), "logs.log", str(p))
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["overall"]["total_lines"] == 10


def test_save_csv(tmp_path):
    p = tmp_path / "r.csv"
    save_csv(make_summary(), "logs.log", str(p))
    with open(p, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["section", "key", "value", "detail"]
    overall = {r[1]: r[2] for r in rows if r[0] == "overall"}
    assert overall["total_lines"] == "10"
    levels = {r[1]: r[2] for r in rows if r[0] == "by_level"}
    assert levels == {"ERROR": "3", "INFO": "3"}
    pe = [r for r in rows if r[0] == "parse_error"]
    assert len(pe) == 2 and pe[0][1] == "line 2"


def test_save_report_dispatch(tmp_path):
    pj = tmp_path / "r.json"
    save_report(make_summary(), "logs.log", str(pj), "json")
    assert pj.exists()
    pc = tmp_path / "r.csv"
    save_report(make_summary(), "logs.log", str(pc), "csv")
    assert pc.exists()


def test_save_report_invalid_format(tmp_path):
    with pytest.raises(ValueError):
        save_report(make_summary(), "logs.log", str(tmp_path / "x"), "xml")


def test_print_summary_output(capsys):
    print_summary(make_summary(), "logs.log", sys.stdout)
    out = capsys.readouterr().out
    assert "Log Analysis Summary" in out
    assert "logs.log" in out
    assert "Total lines:    10" in out
    assert "Line 2" in out
    assert "Line 7" in out