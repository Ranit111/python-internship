"""
Enterprise Automated Sentinel Package.
"""

from sentinel.collector import TelemetryCollector
from sentinel.analyzer import HealthAnalyzer
from sentinel.pdf_generator import PDFReportGenerator
from sentinel.notifier import AlertNotifier
from sentinel.scheduler import AutomatedScheduler

__version__ = "1.0.0"
__all__ = [
    "TelemetryCollector",
    "HealthAnalyzer",
    "PDFReportGenerator",
    "AlertNotifier",
    "AutomatedScheduler",
]
