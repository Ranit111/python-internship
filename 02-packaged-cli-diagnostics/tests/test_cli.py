"""
Integration and functional tests for the CLI runner.
"""

import json
from pathlib import Path
from devdiag.cli import main, run_diagnostics


def test_cli_help(capsys):
    try:
        main(["--help"])
    except SystemExit as e:
        assert e.code == 0
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower() or "devdiag" in captured.out


def test_cli_json_output(capsys):
    exit_code = main(["--json", "-q"])
    assert exit_code in (0, 1, 2)


def test_cli_file_output(tmp_path):
    report_file = tmp_path / "report.json"
    exit_code = main(["--json", "-o", str(report_file), "-q"])
    assert report_file.exists()
    
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "overall_status" in data
    assert "system" in data
    assert "toolchain" in data


def test_cli_missing_events_file():
    exit_code = main(["--events", "non_existent_file.json", "-q"])
    assert exit_code == 2


def test_cli_malformed_events_file(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json content", encoding="utf-8")
    exit_code = main(["--events", str(bad_file), "-q"])
    assert exit_code == 2
