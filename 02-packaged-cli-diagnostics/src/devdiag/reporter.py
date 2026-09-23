"""
Report formatting engine for human-readable terminal display and JSON export.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Dict


class DiagnosticReporter:
    """Formats system diagnostics and toolchain inspection data into text and JSON reports."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def generate_json(self, indent: int = 2) -> str:
        """Serializes health report to a structured JSON string."""
        payload = {
            "schema_version": "1.0.0",
            "timestamp": self.timestamp,
            **self.data,
        }
        return json.dumps(payload, indent=indent)

    def generate_human_readable(self) -> str:
        """Generates a clean, formatted ASCII text report suitable for terminal or file logs."""
        lines = []
        overall_status = self.data.get("overall_status", "UNKNOWN")
        exit_code = self.data.get("exit_code", 0)

        lines.append("=" * 72)
        lines.append("             DEVELOPER ENVIRONMENT HEALTH REPORT")
        lines.append("=" * 72)
        lines.append(f" Timestamp    : {self.timestamp}")
        lines.append(f" Overall Status: [{overall_status}] (Exit Code: {exit_code})")
        lines.append("-" * 72)

        # Python Runtime
        python_data = self.data.get("system", {}).get("python", {})
        lines.append("\n[1] PYTHON RUNTIME & ENVIRONMENT")
        lines.append(f"  * Python Version  : {python_data.get('version')} ({python_data.get('status')})")
        lines.append(f"  * Executable Path : {python_data.get('executable')}")
        lines.append(f"  * Virtualenv Active: {'YES' if python_data.get('in_virtualenv') else 'NO'}")
        if python_data.get("virtualenv_path"):
            lines.append(f"  * Virtualenv Path : {python_data.get('virtualenv_path')}")
        lines.append(f"  * Compiler/Impl   : {python_data.get('implementation')} / {python_data.get('compiler')}")

        # OS & Hardware
        os_data = self.data.get("system", {}).get("os", {})
        res_data = self.data.get("system", {}).get("resources", {})
        disk = res_data.get("disk", {})
        mem = res_data.get("memory", {})
        cpu = res_data.get("cpu", {})

        lines.append("\n[2] OPERATING SYSTEM & HARDWARE RESOURCES")
        lines.append(f"  * OS Platform     : {os_data.get('system')} {os_data.get('release')} ({os_data.get('architecture')})")
        lines.append(f"  * CPU Cores       : {cpu.get('physical_cores')} Physical, {cpu.get('logical_cores')} Logical ({cpu.get('usage_percent')}% utilized)")
        lines.append(f"  * Memory (RAM)    : {mem.get('used_gb')} / {mem.get('total_gb')} GB ({mem.get('percent_used')}%) [{mem.get('status')}]")
        lines.append(f"  * Primary Disk    : {disk.get('free_gb')} GB free of {disk.get('total_gb')} GB ({disk.get('percent_used')}%) [{disk.get('status')}]")

        # Developer Toolchain
        toolchain = self.data.get("toolchain", {})
        tools = toolchain.get("tools", [])
        lines.append("\n[3] CONFIGURED DEVELOPER TOOLCHAIN")
        lines.append(f"  * Tools Checked   : {toolchain.get('total_checked')} (Healthy: {toolchain.get('healthy')}, Warn: {toolchain.get('warnings')}, Fail: {toolchain.get('errors')})")
        for t in tools:
            req_tag = "(Required)" if t.get("required") else "(Optional)"
            status_tag = f"[{t.get('status')}]"
            ver = t.get("version") or "Not Installed"
            lines.append(f"    - {t.get('name'):<10} {status_tag:<9} {req_tag:<11}: {ver}")

        # Diagnostic Events (if present)
        events_data = self.data.get("events")
        if events_data:
            lines.append("\n[4] DIAGNOSTIC EVENT LOG ANALYSIS")
            lines.append(f"  * Total Events    : {events_data.get('total_events')}")
            lines.append(f"  * Overall Status  : [{events_data.get('status')}] (Error Rate: {events_data.get('error_rate_percent')}%)")
            lines.append(f"  * Event Levels    : INFO={events_data.get('levels', {}).get('INFO', 0)}, WARN={events_data.get('levels', {}).get('WARN', 0)}, ERROR={events_data.get('levels', {}).get('ERROR', 0)}")
            lat = events_data.get("latency", {})
            lines.append(f"  * Latency Metrics : Mean={lat.get('mean_ms')}ms | Median={lat.get('median_ms')}ms | Max={lat.get('max_ms')}ms | P90={lat.get('p90_ms')}ms")
            
            services = events_data.get("services", {})
            if services:
                lines.append("  * Service Breakdown:")
                for s_name, s_info in services.items():
                    lines.append(f"      * {s_name:<14}: {s_info.get('total_requests')} reqs, {s_info.get('errors')} errs ({s_info.get('error_rate_pct')}%), avg {s_info.get('avg_latency_ms')}ms [{s_info.get('status')}]")

        lines.append("\n" + "=" * 72)
        lines.append(f" CONCLUSION: Environment is {overall_status}")
        lines.append("=" * 72)
        return "\n".join(lines)
