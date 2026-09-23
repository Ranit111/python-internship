"""
Toolchain and developer binary presence/version checker.
"""

from __future__ import annotations
import shutil
import subprocess
from typing import Any, Dict, List


class ToolchainChecker:
    """Verifies installed developer tools, CLI binaries, and their reported versions."""

    DEFAULT_TOOLS = [
        {"name": "git", "cmd": ["git", "--version"], "required": True},
        {"name": "python", "cmd": ["python", "--version"], "required": True},
        {"name": "pip", "cmd": ["pip", "--version"], "required": True},
        {"name": "pytest", "cmd": ["pytest", "--version"], "required": False},
        {"name": "node", "cmd": ["node", "--version"], "required": False},
        {"name": "npm", "cmd": ["npm", "--version"], "required": False},
        {"name": "docker", "cmd": ["docker", "--version"], "required": False},
        {"name": "rustc", "cmd": ["rustc", "--version"], "required": False},
        {"name": "go", "cmd": ["go", "version"], "required": False},
        {"name": "sqlite3", "cmd": ["sqlite3", "--version"], "required": False},
    ]

    def __init__(self, tool_configs: List[Dict[str, Any]] | None = None) -> None:
        self.tool_configs = tool_configs or self.DEFAULT_TOOLS

    def check_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Checks if a single CLI tool is installed and retrieves its version."""
        binary_name = tool["name"]
        cmd = tool["cmd"]
        is_required = tool.get("required", False)

        resolved_path = shutil.which(cmd[0])
        if not resolved_path:
            return {
                "name": binary_name,
                "installed": False,
                "path": None,
                "version": None,
                "required": is_required,
                "status": "ERROR" if is_required else "WARNING",
                "message": "Required tool missing from PATH" if is_required else "Optional tool not installed",
            }

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            raw_output = (result.stdout or result.stderr).strip().splitlines()
            version_str = raw_output[0] if raw_output else "Unknown version"
            return {
                "name": binary_name,
                "installed": True,
                "path": resolved_path,
                "version": version_str,
                "required": is_required,
                "status": "HEALTHY",
                "message": "Tool operational",
            }
        except Exception as e:
            return {
                "name": binary_name,
                "installed": True,
                "path": resolved_path,
                "version": None,
                "required": is_required,
                "status": "WARNING",
                "message": f"Execution failed: {str(e)}",
            }

    def check_all(self) -> Dict[str, Any]:
        """Checks all configured tools and aggregates the results."""
        results = [self.check_tool(tool) for tool in self.tool_configs]
        healthy_count = sum(1 for r in results if r["status"] == "HEALTHY")
        warning_count = sum(1 for r in results if r["status"] == "WARNING")
        error_count = sum(1 for r in results if r["status"] == "ERROR")

        overall_status = "HEALTHY"
        if error_count > 0:
            overall_status = "ERROR"
        elif warning_count > 0:
            overall_status = "WARNING"

        return {
            "status": overall_status,
            "total_checked": len(results),
            "healthy": healthy_count,
            "warnings": warning_count,
            "errors": error_count,
            "tools": results,
        }
