"""
Unit tests for PDFReportGenerator.
"""

from pathlib import Path
from sentinel.pdf_generator import PDFReportGenerator


def test_build_pdf_report(tmp_path):
    pdf_out = tmp_path / "test_report.pdf"
    generator = PDFReportGenerator(pdf_out, company_name="Test Enterprise")

    telemetry = {
        "system": {
            "os": {"system": "Linux", "release": "6.1", "machine": "x86_64", "python_version": "3.11.9"},
            "cpu": {"usage_percent": 15.0, "physical_cores": 4, "logical_cores": 8},
            "memory": {"usage_percent": 42.0, "used_gb": 6.5, "total_gb": 16.0},
            "disk": {"usage_percent": 65.0, "used_gb": 150.0, "total_gb": 500.0, "free_gb": 350.0},
        },
        "endpoints": [
            {"name": "Auth API", "status_code": 200, "latency_ms": 110.0, "is_healthy": True}
        ],
    }
    evaluation = {
        "overall_status": "OPTIMAL",
        "health_score": 100,
        "grade": "GRADE A+ (Fully Operational)",
        "warnings_count": 0,
        "critical_count": 0,
        "anomalies": [],
    }

    built_path = generator.build_report(telemetry, evaluation)
    assert built_path.exists()
    assert built_path.stat().st_size > 1000  # Non-empty binary PDF
