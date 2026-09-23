"""
Health analyzer and anomaly detection engine evaluating telemetry against SLA thresholds.
"""

from __future__ import annotations
from typing import Any, Dict, List


class HealthAnalyzer:
    """Evaluates telemetry data against operational thresholds to detect anomalies and assign grades."""

    DEFAULT_THRESHOLDS = {
        "cpu_warning_pct": 75.0,
        "cpu_critical_pct": 90.0,
        "memory_warning_pct": 80.0,
        "memory_critical_pct": 92.0,
        "disk_warning_pct": 85.0,
        "disk_critical_pct": 95.0,
        "api_latency_max_ms": 1500.0,
    }

    def __init__(self, thresholds: Dict[str, float] | None = None) -> None:
        self.thresholds = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}

    def evaluate(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes system metrics and endpoint results, returning health score, grade, and anomalies."""
        sys_data = telemetry.get("system", {})
        endpoints_data = telemetry.get("endpoints", [])

        anomalies: List[Dict[str, str]] = []
        warnings_count = 0
        critical_count = 0

        # 1. CPU Check
        cpu_usage = sys_data.get("cpu", {}).get("usage_percent", 0.0)
        if cpu_usage >= self.thresholds["cpu_critical_pct"]:
            critical_count += 1
            anomalies.append({"severity": "CRITICAL", "component": "CPU", "message": f"CPU usage critical at {cpu_usage}%"})
        elif cpu_usage >= self.thresholds["cpu_warning_pct"]:
            warnings_count += 1
            anomalies.append({"severity": "WARNING", "component": "CPU", "message": f"CPU usage elevated at {cpu_usage}%"})

        # 2. Memory Check
        mem_usage = sys_data.get("memory", {}).get("usage_percent", 0.0)
        if mem_usage >= self.thresholds["memory_critical_pct"]:
            critical_count += 1
            anomalies.append({"severity": "CRITICAL", "component": "RAM", "message": f"Memory critical at {mem_usage}%"})
        elif mem_usage >= self.thresholds["memory_warning_pct"]:
            warnings_count += 1
            anomalies.append({"severity": "WARNING", "component": "RAM", "message": f"Memory elevated at {mem_usage}%"})

        # 3. Disk Check
        disk_usage = sys_data.get("disk", {}).get("usage_percent", 0.0)
        if disk_usage >= self.thresholds["disk_critical_pct"]:
            critical_count += 1
            anomalies.append({"severity": "CRITICAL", "component": "DISK", "message": f"Disk space critically low ({disk_usage}% full)"})
        elif disk_usage >= self.thresholds["disk_warning_pct"]:
            warnings_count += 1
            anomalies.append({"severity": "WARNING", "component": "DISK", "message": f"Disk space elevated ({disk_usage}% full)"})

        # 4. Endpoint Checks
        for ep in endpoints_data:
            if not ep.get("is_healthy", False):
                critical_count += 1
                anomalies.append({
                    "severity": "CRITICAL",
                    "component": f"API:{ep.get('name')}",
                    "message": f"Endpoint unreachable or returned error: {ep.get('error')}",
                })
            elif ep.get("latency_ms", 0.0) > self.thresholds["api_latency_max_ms"]:
                warnings_count += 1
                anomalies.append({
                    "severity": "WARNING",
                    "component": f"API:{ep.get('name')}",
                    "message": f"High response latency ({ep.get('latency_ms')} ms)",
                })

        # Score & Grade Calculation
        if critical_count > 0:
            health_score = max(20, 100 - (critical_count * 30) - (warnings_count * 10))
            overall_status = "CRITICAL"
            grade = "GRADE D (Critical Incidents)" if critical_count == 1 else "GRADE F (Major Outage)"
        elif warnings_count > 0:
            health_score = max(65, 100 - (warnings_count * 10))
            overall_status = "WARNING"
            grade = "GRADE B (Degraded Performance)"
        else:
            health_score = 100
            overall_status = "OPTIMAL"
            grade = "GRADE A+ (Fully Operational)"

        return {
            "overall_status": overall_status,
            "grade": grade,
            "health_score": health_score,
            "warnings_count": warnings_count,
            "critical_count": critical_count,
            "anomalies": anomalies,
            "is_action_required": (critical_count > 0 or warnings_count > 0),
        }
