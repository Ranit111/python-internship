"""
Unit tests for TelemetryCollector.
"""

from unittest.mock import MagicMock, patch
from sentinel.collector import TelemetryCollector


def test_collect_system_metrics():
    collector = TelemetryCollector()
    metrics = collector.collect_system_metrics()

    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    assert "os" in metrics
    assert metrics["cpu"]["usage_percent"] >= 0.0
    assert metrics["memory"]["total_gb"] > 0.0
    assert metrics["disk"]["total_gb"] > 0.0


def test_check_endpoints_mocked():
    endpoints = [
        {"name": "Test API", "url": "https://api.example.com/health", "expected_status": 200, "timeout": 2.0}
    ]
    collector = TelemetryCollector(endpoints=endpoints)

    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        results = collector.check_endpoints()
        assert len(results) == 1
        assert results[0]["name"] == "Test API"
        assert results[0]["is_healthy"] is True
        assert results[0]["status_code"] == 200
