"""
Unit tests for EventAnalyzer.
"""

import json
import pytest
from pathlib import Path
from devdiag.event_analyzer import EventAnalyzer, MalformedEventFileError


def test_analyze_official_sample(tmp_path):
    sample_file = tmp_path / "events.json"
    sample_data = {
        "events": [
            { "timestamp": "2026-08-01T09:00:00Z", "service": "billing-api", "level": "INFO", "latency_ms": 148, "status_code": 200 },
            { "timestamp": "2026-08-01T09:01:00Z", "service": "billing-api", "level": "WARN", "latency_ms": 920, "status_code": 200 },
            { "timestamp": "2026-08-01T09:02:00Z", "service": "profile-api", "level": "ERROR", "latency_ms": 1210, "status_code": 503 },
            { "timestamp": "2026-08-01T09:03:00Z", "service": "profile-api", "level": "INFO", "latency_ms": 205, "status_code": 200 },
            { "timestamp": "2026-08-01T09:04:00Z", "service": "billing-api", "level": "ERROR", "latency_ms": None, "status_code": 500 }
        ]
    }
    sample_file.write_text(json.dumps(sample_data), encoding="utf-8")

    analyzer = EventAnalyzer(sample_file)
    metrics = analyzer.analyze()

    assert metrics["total_events"] == 5
    assert metrics["levels"]["ERROR"] == 2
    assert metrics["levels"]["WARN"] == 1
    assert metrics["levels"]["INFO"] == 2
    assert metrics["error_rate_percent"] == 40.0
    assert metrics["status"] == "ERROR"
    assert "billing-api" in metrics["services"]
    assert "profile-api" in metrics["services"]
    assert metrics["latency"]["count"] == 4
    assert metrics["latency"]["min_ms"] == 148.0
    assert metrics["latency"]["max_ms"] == 1210.0


def test_missing_event_file():
    analyzer = EventAnalyzer("non_existent_file_path.json")
    with pytest.raises(FileNotFoundError):
        analyzer.load_events()


def test_malformed_json_file(tmp_path):
    bad_file = tmp_path / "corrupted.json"
    bad_file.write_text("{ unclosed json structure", encoding="utf-8")
    analyzer = EventAnalyzer(bad_file)
    with pytest.raises(MalformedEventFileError):
        analyzer.load_events()


def test_empty_events_list():
    analyzer = EventAnalyzer()
    metrics = analyzer.analyze([])
    assert metrics["total_events"] == 0
    assert metrics["status"] == "HEALTHY"
