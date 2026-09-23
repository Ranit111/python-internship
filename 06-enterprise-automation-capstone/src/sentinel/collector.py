"""
Multi-source telemetry collector gathering system metrics and endpoint health.
"""

from __future__ import annotations
import os
import platform
import time
from typing import Any, Dict, List, Optional
import psutil
import requests


class TelemetryCollector:
    """Collects machine runtime statistics, process metrics, and remote API liveness."""

    def __init__(self, endpoints: Optional[List[Dict[str, Any]]] = None) -> None:
        self.endpoints = endpoints or []

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Gathers CPU, memory, disk, network, and OS telemetry."""
        # CPU
        cpu_pct = psutil.cpu_percent(interval=0.1)
        cpu_count_logical = psutil.cpu_count(logical=True) or 1
        cpu_count_physical = psutil.cpu_count(logical=False) or cpu_count_logical

        # Memory
        mem = psutil.virtual_memory()
        mem_total_gb = round(mem.total / (1024**3), 2)
        mem_used_gb = round(mem.used / (1024**3), 2)
        mem_available_gb = round(mem.available / (1024**3), 2)
        mem_pct = mem.percent

        # Disk
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        disk_total_gb = round(disk.total / (1024**3), 2)
        disk_used_gb = round(disk.used / (1024**3), 2)
        disk_free_gb = round(disk.free / (1024**3), 2)
        disk_pct = disk.percent

        return {
            "timestamp": time.time(),
            "os": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
            "cpu": {
                "usage_percent": cpu_pct,
                "physical_cores": cpu_count_physical,
                "logical_cores": cpu_count_logical,
            },
            "memory": {
                "total_gb": mem_total_gb,
                "used_gb": mem_used_gb,
                "available_gb": mem_available_gb,
                "usage_percent": mem_pct,
            },
            "disk": {
                "total_gb": disk_total_gb,
                "used_gb": disk_used_gb,
                "free_gb": disk_free_gb,
                "usage_percent": disk_pct,
            },
        }

    def check_endpoints(self) -> List[Dict[str, Any]]:
        """Probes configured remote API endpoints to measure response latency and availability."""
        results = []
        for ep in self.endpoints:
            name = ep.get("name", "Unnamed Endpoint")
            url = ep.get("url", "")
            expected_status = ep.get("expected_status", 200)
            timeout = float(ep.get("timeout", 3.0))

            start_t = time.time()
            try:
                # Use HEAD or quick GET
                resp = requests.get(url, timeout=timeout)
                latency_ms = round((time.time() - start_t) * 1000, 2)
                is_ok = (resp.status_code == expected_status)
                results.append({
                    "name": name,
                    "url": url,
                    "status_code": resp.status_code,
                    "latency_ms": latency_ms,
                    "is_healthy": is_ok,
                    "error": None if is_ok else f"Expected {expected_status}, got {resp.status_code}",
                })
            except requests.RequestException as e:
                latency_ms = round((time.time() - start_t) * 1000, 2)
                results.append({
                    "name": name,
                    "url": url,
                    "status_code": 0,
                    "latency_ms": latency_ms,
                    "is_healthy": False,
                    "error": str(e),
                })

        return results

    def collect_all(self) -> Dict[str, Any]:
        """Runs full telemetry aggregation."""
        return {
            "system": self.collect_system_metrics(),
            "endpoints": self.check_endpoints(),
        }
