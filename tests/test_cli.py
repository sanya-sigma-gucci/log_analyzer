from __future__ import annotations

import json

import pytest

from log_analyzer.cli import main


def _write_log(path):
    path.write_text(
        "2026-09-01T00:08:59Z | WARN | auth-api | AUTH_LOGIN_OK | User session created\n"
        "2026-09-01T00:20:18Z | ERROR | payment-worker | PAYMENT_TIMEOUT | Payment provider timed out\n"
        "bad line\n"
        "2026-09-01T00:47:04Z | INFO | auth-api | AUTH_TOKEN_EXPIRED | Access token expired\n",
        encoding="utf-8",
    )


def test_cli_basic(tmp_path, capsys):
    p = tmp_path / "logs.log"
    _write_log(p)
    rc = main(["--input", str(p)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Total lines:    4" in out
    assert "Valid lines:    3" in out
    assert "Invalid lines:  1" in out
    assert "Filtered:       3" in out


def test_cli_json_output(tmp_path, capsys):
    p = tmp_path / "logs.log"
    out = tmp_path / "report.json"
    _write_log(p)
    rc = main(["--input", str(p), "--output", str(out), "--format", "json"])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["overall"]["total_lines"] == 4
    assert data["overall"]["filtered_events"] == 3


def test_cli_csv_output(tmp_path, capsys):
    p = tmp_path / "logs.log"
    out = tmp_path / "report.csv"
    _write_log(p)
    rc = main(["--input", str(p), "--output", str(out), "--format", "csv"])
    assert rc == 0
    content = out.read_text(encoding="utf-8")
    assert "section,key,value,detail" in content
    assert "total_lines,4" in content


def test_cli_missing_file(tmp_path, capsys):
    rc = main(["--input", str(tmp_path / "missing.log")])
    assert rc == 2
    err = capsys.readouterr().err
    assert "not found" in err.lower()


def test_cli_directory_input(tmp_path, capsys):
    rc = main(["--input", str(tmp_path)])
    assert rc == 2
    err = capsys.readouterr().err.lower()
    assert "cannot read" in err or "error" in err


def test_cli_empty_file(tmp_path, capsys):
    p = tmp_path / "empty.log"
    p.write_text("", encoding="utf-8")
    rc = main(["--input", str(p)])
    assert rc == 0
    assert "Total lines:    0" in capsys.readouterr().out


def test_cli_invalid_level(tmp_path):
    p = tmp_path / "logs.log"
    _write_log(p)
    with pytest.raises(SystemExit) as exc:
        main(["--input", str(p), "--level", "FATAL"])
    assert exc.value.code == 2


def test_cli_invalid_timestamp(tmp_path):
    p = tmp_path / "logs.log"
    _write_log(p)
    with pytest.raises(SystemExit) as exc:
        main(["--input", str(p), "--from", "not-a-date"])
    assert exc.value.code == 2


def test_cli_negative_top(tmp_path):
    p = tmp_path / "logs.log"
    _write_log(p)
    with pytest.raises(SystemExit):
        main(["--input", str(p), "--top", "-1"])


def test_cli_with_filters(tmp_path, capsys):
    p = tmp_path / "logs.log"
    _write_log(p)
    rc = main([
        "--input", str(p),
        "--from", "2026-09-01T00:10:00Z",
        "--to", "2026-09-01T01:00:00Z",
        "--level", "ERROR",
        "--source", "payment-worker",
    ])
    assert rc == 0
    assert "Filtered:       1" in capsys.readouterr().out


def test_cli_top_zero_all(tmp_path, capsys):
    p = tmp_path / "logs.log"
    _write_log(p)
    rc = main(["--input", str(p), "--top", "0"])
    assert rc == 0


def test_cli_output_error(tmp_path, capsys):
    p = tmp_path / "logs.log"
    _write_log(p)
    out_dir = tmp_path / "out_dir"
    out_dir.mkdir()
    rc = main(["--input", str(p), "--output", str(out_dir)])
    assert rc == 3