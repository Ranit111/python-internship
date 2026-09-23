"""
Unit tests for ToolchainChecker.
"""

from unittest.mock import patch
from devdiag.toolchain_checker import ToolchainChecker


def test_check_tool_found():
    checker = ToolchainChecker()
    tool = {"name": "python", "cmd": ["python", "--version"], "required": True}
    res = checker.check_tool(tool)
    assert res["installed"] is True
    assert res["status"] == "HEALTHY"
    assert res["version"] is not None


def test_check_tool_missing_required():
    checker = ToolchainChecker()
    tool = {"name": "non_existent_binary_xyz_123", "cmd": ["non_existent_binary_xyz_123", "--version"], "required": True}
    res = checker.check_tool(tool)
    assert res["installed"] is False
    assert res["status"] == "ERROR"
    assert res["required"] is True


def test_check_tool_missing_optional():
    checker = ToolchainChecker()
    tool = {"name": "non_existent_optional_tool", "cmd": ["non_existent_optional_tool", "--version"], "required": False}
    res = checker.check_tool(tool)
    assert res["installed"] is False
    assert res["status"] == "WARNING"
    assert res["required"] is False


def test_check_all_aggregation():
    custom_tools = [
        {"name": "python", "cmd": ["python", "--version"], "required": True},
        {"name": "fake_opt", "cmd": ["non_existent_fake_cmd"], "required": False},
    ]
    checker = ToolchainChecker(custom_tools)
    result = checker.check_all()
    assert result["total_checked"] == 2
    assert result["healthy"] >= 1
    assert result["warnings"] == 1
    assert result["status"] == "WARNING"
