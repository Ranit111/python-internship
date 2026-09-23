"""
Notification and alert dispatcher supporting Console and Webhooks/Slack.
"""

from __future__ import annotations
import json
import logging
from typing import Any, Dict
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger("sentinel.notifier")


class AlertNotifier:
    """Dispatches real-time alerts and health event summaries across communication channels."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {
            "enable_console": True,
            "enable_webhook": False,
            "webhook_url": None,
            "alert_on_warning": True,
            "alert_on_critical": True,
        }
        self.console = Console()

    def send_alert(self, evaluation: Dict[str, Any], telemetry: Dict[str, Any]) -> Dict[str, bool]:
        """Dispatches alerts to configured channels based on evaluation severity."""
        results = {"console": False, "webhook": False}
        status = evaluation.get("overall_status", "UNKNOWN")
        is_action_req = evaluation.get("is_action_required", False)

        # 1. Console Dispatch
        if self.config.get("enable_console", True):
            self._render_console_summary(evaluation, telemetry)
            results["console"] = True

        # 2. Webhook Dispatch (Slack / Discord / OpsGenie)
        webhook_url = self.config.get("webhook_url")
        if self.config.get("enable_webhook", False) and webhook_url and is_action_req:
            payload = {
                "text": f"🚨 [Sentinel Alert] System status is {status} (Score: {evaluation.get('health_score')}/100)",
                "status": status,
                "grade": evaluation.get("grade"),
                "anomalies": evaluation.get("anomalies", []),
            }
            try:
                resp = requests.post(webhook_url, json=payload, timeout=5)
                results["webhook"] = (resp.status_code in (200, 201, 204))
            except Exception as e:
                logger.error("Failed sending webhook alert: %s", e)
                results["webhook"] = False

        return results

    def _render_console_summary(self, evaluation: Dict[str, Any], telemetry: Dict[str, Any]) -> None:
        """Renders rich terminal summary."""
        status = evaluation.get("overall_status")
        score = evaluation.get("health_score")
        color = "green" if status == "OPTIMAL" else ("yellow" if status == "WARNING" else "red")

        table = Table(title=f"Enterprise Sentinel Health Status: [{color}]{status}[/{color}] (Score: {score}/100)")
        table.add_column("Category", style="cyan")
        table.add_column("Metrics", style="magenta")
        table.add_column("Status", style="green")

        sys_data = telemetry.get("system", {})
        table.add_row("CPU Utilization", f"{sys_data.get('cpu', {}).get('usage_percent')}%", "Nominal")
        table.add_row("RAM Utilization", f"{sys_data.get('memory', {}).get('usage_percent')}%", "Nominal")
        table.add_row("Disk Utilization", f"{sys_data.get('disk', {}).get('usage_percent')}%", "Nominal")

        self.console.print(table)
