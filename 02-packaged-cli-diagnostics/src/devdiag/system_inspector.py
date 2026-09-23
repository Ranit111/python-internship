"""
System environment inspector for Python runtime, OS, disk, memory, and environment variables.
"""

from __future__ import annotations
import os
import platform
import sys
from typing import Any, Dict, List
import psutil


class SystemInspector:
    """Collects machine runtime metrics, hardware resources, and environment parameters."""

    SENSITIVE_PATTERNS = ("KEY", "SECRET", "TOKEN", "PASS", "AUTH", "CREDENTIAL", "PRIVATE")

    def __init__(self, disk_path: str | None = None) -> None:
        self.disk_path = disk_path or os.path.abspath(os.sep)

    def inspect_python(self) -> Dict[str, Any]:
        """Inspects Python interpreter details, virtualenv status, and path."""
        is_venv = (
            hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
            or bool(os.environ.get("VIRTUAL_ENV"))
        )

        version_info = sys.version_info
        is_supported = version_info >= (3, 9)

        return {
            "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            "executable": sys.executable,
            "in_virtualenv": is_venv,
            "virtualenv_path": os.environ.get("VIRTUAL_ENV"),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
            "is_supported": is_supported,
            "status": "HEALTHY" if is_supported else "ERROR",
            "message": "Python version >= 3.9" if is_supported else "Python >= 3.9 is required",
        }

    def inspect_os(self) -> Dict[str, Any]:
        """Inspects operating system information and architecture."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor() or "Unknown",
        }

    def inspect_resources(self) -> Dict[str, Any]:
        """Inspects disk space, memory, and CPU utilization with health status."""
        # Disk Space
        try:
            disk = psutil.disk_usage(self.disk_path)
            disk_total_gb = round(disk.total / (1024**3), 2)
            disk_free_gb = round(disk.free / (1024**3), 2)
            disk_used_gb = round(disk.used / (1024**3), 2)
            disk_percent = disk.percent
        except Exception:
            disk_total_gb, disk_free_gb, disk_used_gb, disk_percent = 0.0, 0.0, 0.0, 0.0

        if disk_percent >= 95.0:
            disk_status = "ERROR"
            disk_msg = f"Disk usage critically high ({disk_percent}% used)"
        elif disk_percent >= 85.0:
            disk_status = "WARNING"
            disk_msg = f"Disk usage elevated ({disk_percent}% used)"
        else:
            disk_status = "HEALTHY"
            disk_msg = f"Disk space healthy ({disk_free_gb} GB free)"

        # Memory (RAM)
        try:
            mem = psutil.virtual_memory()
            mem_total_gb = round(mem.total / (1024**3), 2)
            mem_available_gb = round(mem.available / (1024**3), 2)
            mem_used_gb = round(mem.used / (1024**3), 2)
            mem_percent = mem.percent
        except Exception:
            mem_total_gb, mem_available_gb, mem_used_gb, mem_percent = 0.0, 0.0, 0.0, 0.0

        if mem_percent >= 95.0:
            mem_status = "ERROR"
            mem_msg = f"RAM critically high ({mem_percent}% used)"
        elif mem_percent >= 85.0:
            mem_status = "WARNING"
            mem_msg = f"RAM usage elevated ({mem_percent}% used)"
        else:
            mem_status = "HEALTHY"
            mem_msg = f"Memory healthy ({mem_available_gb} GB available)"

        # CPU
        try:
            cpu_count_logical = psutil.cpu_count(logical=True) or 1
            cpu_count_physical = psutil.cpu_count(logical=False) or cpu_count_logical
            cpu_percent = psutil.cpu_percent(interval=0.1)
        except Exception:
            cpu_count_logical, cpu_count_physical, cpu_percent = 1, 1, 0.0

        return {
            "disk": {
                "path": self.disk_path,
                "total_gb": disk_total_gb,
                "used_gb": disk_used_gb,
                "free_gb": disk_free_gb,
                "percent_used": disk_percent,
                "status": disk_status,
                "message": disk_msg,
            },
            "memory": {
                "total_gb": mem_total_gb,
                "used_gb": mem_used_gb,
                "available_gb": mem_available_gb,
                "percent_used": mem_percent,
                "status": mem_status,
                "message": mem_msg,
            },
            "cpu": {
                "physical_cores": cpu_count_physical,
                "logical_cores": cpu_count_logical,
                "usage_percent": cpu_percent,
            },
        }

    def inspect_environment(self) -> Dict[str, Any]:
        """Audits environment variables, redacting sensitive tokens and secrets."""
        tracked_keys = [
            "PATH", "PYTHONPATH", "VIRTUAL_ENV", "HOME", "USERPROFILE",
            "SHELL", "COMSPEC", "TERM", "LANG", "NODE_ENV", "PYTHONUNBUFFERED"
        ]
        
        audited_vars: Dict[str, str] = {}
        for key, value in sorted(os.environ.items()):
            upper_key = key.upper()
            if any(sensitive in upper_key for sensitive in self.SENSITIVE_PATTERNS):
                audited_vars[key] = "******** [REDACTED SECRET]"
            elif key in tracked_keys or upper_key.startswith("DEV_") or upper_key.startswith("PYTHON"):
                if len(value) > 120 and key == "PATH":
                    paths = value.split(os.pathsep)
                    audited_vars[key] = f"[{len(paths)} entries: {paths[0]} ... {paths[-1]}]"
                else:
                    audited_vars[key] = value

        return {
            "total_vars_count": len(os.environ),
            "audited_variables": audited_vars,
            "has_virtualenv_set": bool(os.environ.get("VIRTUAL_ENV")),
        }

    def run_full_inspection(self) -> Dict[str, Any]:
        """Runs complete system inspection and returns structured dictionary."""
        return {
            "python": self.inspect_python(),
            "os": self.inspect_os(),
            "resources": self.inspect_resources(),
            "environment": self.inspect_environment(),
        }
