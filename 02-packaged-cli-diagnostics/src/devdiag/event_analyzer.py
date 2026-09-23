"""
Diagnostic event log parser and metrics analyzer.
"""

from __future__ import annotations
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional


class MalformedEventFileError(Exception):
    """Raised when the event file format is invalid or unparseable."""
    pass


class EventAnalyzer:
    """Analyzes structured machine/service diagnostic logs and computes telemetry KPIs."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        self.file_path = Path(file_path) if file_path else None

    def load_events(self) -> List[Dict[str, Any]]:
        """Loads and validates events from the target JSON file."""
        if not self.file_path:
            return []
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Diagnostic event file not found: {self.file_path}")

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise MalformedEventFileError(f"Invalid JSON in event log: {e}") from e

        if isinstance(data, dict) and "events" in data:
            events = data["events"]
        elif isinstance(data, list):
            events = data
        else:
            raise MalformedEventFileError("JSON payload must be a list of events or contain an 'events' key.")

        if not isinstance(events, list):
            raise MalformedEventFileError("'events' property must be a list.")

        return events

    def analyze(self, events: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculates error rates, latency distribution, and service-level health metrics."""
        if events is None:
            events = self.load_events()

        total_events = len(events)
        if total_events == 0:
            return {
                "total_events": 0,
                "status": "HEALTHY",
                "message": "No events recorded",
                "metrics": {},
                "services": {},
            }

        level_counts: Dict[str, int] = {"INFO": 0, "WARN": 0, "ERROR": 0}
        status_code_counts: Dict[int, int] = {}
        latencies: List[float] = []
        service_stats: Dict[str, Dict[str, Any]] = {}

        for ev in events:
            if not isinstance(ev, dict):
                raise MalformedEventFileError("Individual event entry must be a dictionary.")

            level = str(ev.get("level", "INFO")).upper()
            level_counts[level] = level_counts.get(level, 0) + 1

            status_code = ev.get("status_code")
            if isinstance(status_code, int):
                status_code_counts[status_code] = status_code_counts.get(status_code, 0) + 1

            latency = ev.get("latency_ms")
            if latency is not None and isinstance(latency, (int, float)):
                latencies.append(float(latency))

            service_name = str(ev.get("service", "unknown"))
            if service_name not in service_stats:
                service_stats[service_name] = {
                    "total": 0,
                    "errors": 0,
                    "warnings": 0,
                    "latencies": [],
                }
            
            service_stats[service_name]["total"] += 1
            if level == "ERROR":
                service_stats[service_name]["errors"] += 1
            elif level == "WARN":
                service_stats[service_name]["warnings"] += 1
            
            if latency is not None and isinstance(latency, (int, float)):
                service_stats[service_name]["latencies"].append(float(latency))

        # Latency statistics
        if latencies:
            sorted_lat = sorted(latencies)
            latency_summary = {
                "count": len(latencies),
                "min_ms": round(min(latencies), 2),
                "max_ms": round(max(latencies), 2),
                "mean_ms": round(statistics.mean(latencies), 2),
                "median_ms": round(statistics.median(latencies), 2),
                "p90_ms": round(sorted_lat[int(len(sorted_lat) * 0.9)], 2) if len(sorted_lat) >= 10 else round(max(latencies), 2),
            }
        else:
            latency_summary = {"count": 0, "min_ms": 0.0, "max_ms": 0.0, "mean_ms": 0.0, "median_ms": 0.0, "p90_ms": 0.0}

        # Service metrics transformation
        processed_services = {}
        for s_name, s_data in service_stats.items():
            s_lat = s_data["latencies"]
            s_mean_lat = round(statistics.mean(s_lat), 2) if s_lat else 0.0
            error_rate = round((s_data["errors"] / s_data["total"]) * 100, 2)
            
            s_status = "HEALTHY"
            if error_rate > 20.0:
                s_status = "ERROR"
            elif error_rate > 0.0 or s_data["warnings"] > 0:
                s_status = "WARNING"

            processed_services[s_name] = {
                "total_requests": s_data["total"],
                "errors": s_data["errors"],
                "warnings": s_data["warnings"],
                "error_rate_pct": error_rate,
                "avg_latency_ms": s_mean_lat,
                "status": s_status,
            }

        error_rate_total = round((level_counts.get("ERROR", 0) / total_events) * 100, 2)
        overall_status = "HEALTHY"
        if error_rate_total >= 20.0 or level_counts.get("ERROR", 0) >= 2:
            overall_status = "ERROR"
        elif error_rate_total > 0.0 or level_counts.get("WARN", 0) > 0:
            overall_status = "WARNING"

        return {
            "total_events": total_events,
            "error_rate_percent": error_rate_total,
            "levels": level_counts,
            "status_codes": status_code_counts,
            "latency": latency_summary,
            "services": processed_services,
            "status": overall_status,
        }
