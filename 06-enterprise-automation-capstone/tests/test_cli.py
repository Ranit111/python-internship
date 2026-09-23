"""
Unit tests for Sentinel CLI interface.
"""

from pathlib import Path
from unittest.mock import patch
from sentinel.cli import main


def test_cli_verify_config(capsys):
    exit_code = main(["verify-config"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "[OK]" in captured.out


def test_cli_run_once(tmp_path):
    report_pdf = tmp_path / "cli_report.pdf"
    exit_code = main(["run-once"])
    assert exit_code == 0


def test_cli_generate_report(tmp_path):
    out_pdf = tmp_path / "custom_report.pdf"
    exit_code = main(["generate-report", "-o", str(out_pdf)])
    assert exit_code == 0
    assert out_pdf.exists()


def test_cli_schedule_max_cycles():
    exit_code = main(["schedule", "-i", "1", "-m", "1"])
    assert exit_code == 0
