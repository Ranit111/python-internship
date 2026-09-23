"""
Unit tests for SystemInspector.
"""

import os
from devdiag.system_inspector import SystemInspector


def test_inspect_python():
    inspector = SystemInspector()
    result = inspector.inspect_python()
    assert "version" in result
    assert "executable" in result
    assert "in_virtualenv" in result
    assert result["is_supported"] is True
    assert result["status"] == "HEALTHY"


def test_inspect_os():
    inspector = SystemInspector()
    result = inspector.inspect_os()
    assert "system" in result
    assert "release" in result
    assert "machine" in result


def test_inspect_resources():
    inspector = SystemInspector()
    result = inspector.inspect_resources()
    assert "disk" in result
    assert "memory" in result
    assert "cpu" in result
    assert result["disk"]["total_gb"] > 0
    assert result["memory"]["total_gb"] > 0
    assert result["cpu"]["logical_cores"] >= 1


def test_inspect_environment_masks_secrets(monkeypatch):
    monkeypatch.setenv("AWS_SECRET_KEY", "super_secret_value_12345")
    monkeypatch.setenv("DATABASE_PASSWORD", "db_password_xyz")
    monkeypatch.setenv("API_TOKEN", "token_abcdef")
    monkeypatch.setenv("DEV_MODE", "enabled")

    inspector = SystemInspector()
    result = inspector.inspect_environment()
    audited = result["audited_variables"]

    assert "AWS_SECRET_KEY" in audited
    assert "super_secret" not in audited["AWS_SECRET_KEY"]
    assert "REDACTED" in audited["AWS_SECRET_KEY"]

    assert "DATABASE_PASSWORD" in audited
    assert "REDACTED" in audited["DATABASE_PASSWORD"]

    assert "DEV_MODE" in audited
    assert audited["DEV_MODE"] == "enabled"
