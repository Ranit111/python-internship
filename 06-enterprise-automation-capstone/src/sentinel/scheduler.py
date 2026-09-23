"""
Automated background task scheduler orchestrating periodic health checks.
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from sentinel.analyzer import HealthAnalyzer
from sentinel.collector import TelemetryCollector
from sentinel.notifier import AlertNotifier
from sentinel.pdf_generator import PDFReportGenerator

logger = logging.getLogger("sentinel.scheduler")


class AutomatedScheduler:
    """Orchestrates recurring telemetry collection, PDF generation, and alert dispatching."""

    def __init__(self, config: Dict[str, Any], config_dir: Optional[Path] = None) -> None:
        self.config = config
        self.base_dir = config_dir or Path.cwd()
        
        self.collector = TelemetryCollector(endpoints=config.get("endpoints", []))
        self.analyzer = HealthAnalyzer(thresholds=config.get("thresholds", {}))
        
        pdf_path = self.base_dir / config.get("reporting", {}).get("output_pdf", "output/report.pdf")
        company = config.get("reporting", {}).get("company_name", "Enterprise Systems")
        self.pdf_generator = PDFReportGenerator(pdf_path, company_name=company)
        self.notifier = AlertNotifier(config=config.get("notification", {}))

    def run_single_cycle(self) -> Dict[str, Any]:
        """Executes one complete health check, PDF generation, and notification cycle."""
        # 1. Collect
        telemetry = self.collector.collect_all()

        # 2. Analyze
        evaluation = self.analyzer.evaluate(telemetry)

        # 3. Generate PDF
        pdf_file = self.pdf_generator.build_report(telemetry, evaluation)

        # 4. Notify
        notify_res = self.notifier.send_alert(evaluation, telemetry)

        return {
            "telemetry": telemetry,
            "evaluation": evaluation,
            "pdf_path": str(pdf_file),
            "notification": notify_res,
        }

    def start_loop(self, interval_seconds: int = 60, max_cycles: Optional[int] = None) -> None:
        """Runs the continuous scheduler loop for automated daemon execution."""
        cycle_count = 0
        print(f"[*] Starting Sentinel Automated Scheduler (Interval: {interval_seconds}s)")
        try:
            while True:
                cycle_count += 1
                print(f"\n[+] Executing Sentinel Automation Cycle #{cycle_count}")
                result = self.run_single_cycle()
                print(f"    - Health Status: {result['evaluation']['overall_status']} (Score: {result['evaluation']['health_score']}/100)")
                print(f"    - Generated PDF: {result['pdf_path']}")

                if max_cycles and cycle_count >= max_cycles:
                    print(f"[*] Reached max cycles ({max_cycles}). Exiting gracefully.")
                    break

                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[*] Scheduler stopped by user.")
