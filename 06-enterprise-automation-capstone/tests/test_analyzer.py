"""
Unit tests for HealthAnalyzer and anomaly scoring.
"""

from sentinel.analyzer import HealthAnalyzer


def test_evaluate_optimal():
    telemetry = {
        "system": {
            "cpu": {"usage_percent": 25.0},
            "memory": {"usage_percent": 45.0},
            "disk": {"usage_percent": 50.0},
        },
        "endpoints": [
            {"name": "API 1", "is_healthy": True, "latency_ms": 120.0}
        ],
    }
    analyzer = HealthAnalyzer()
    eval_res = analyzer.evaluate(telemetry)

    assert eval_res["overall_status"] == "OPTIMAL"
    assert eval_res["health_score"] == 100
    assert "GRADE A+" in eval_res["grade"]
    assert len(eval_res["anomalies"]) == 0


def test_evaluate_critical():
    telemetry = {
        "system": {
            "cpu": {"usage_percent": 95.0}, # Critical CPU
            "memory": {"usage_percent": 60.0},
            "disk": {"usage_percent": 60.0},
        },
        "endpoints": [
            {"name": "Payment API", "is_healthy": False, "error": "Connection Timeout"} # Critical API
        ],
    }
    analyzer = HealthAnalyzer()
    eval_res = analyzer.evaluate(telemetry)

    assert eval_res["overall_status"] == "CRITICAL"
    assert eval_res["critical_count"] == 2
    assert eval_res["health_score"] <= 40
    assert len(eval_res["anomalies"]) == 2
