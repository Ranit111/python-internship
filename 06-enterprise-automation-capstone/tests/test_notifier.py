"""
Unit tests for AlertNotifier.
"""

from unittest.mock import MagicMock, patch
from sentinel.notifier import AlertNotifier


def test_send_console_alert():
    notifier = AlertNotifier({"enable_console": True, "enable_webhook": False})
    eval_data = {"overall_status": "OPTIMAL", "health_score": 100, "is_action_required": False}
    telemetry = {"system": {"cpu": {"usage_percent": 10}, "memory": {"usage_percent": 20}, "disk": {"usage_percent": 30}}}

    res = notifier.send_alert(eval_data, telemetry)
    assert res["console"] is True
    assert res["webhook"] is False


def test_send_webhook_alert_mocked():
    notifier = AlertNotifier({
        "enable_console": False,
        "enable_webhook": True,
        "webhook_url": "https://hooks.slack.com/services/mock",
    })
    eval_data = {
        "overall_status": "CRITICAL",
        "health_score": 30,
        "grade": "GRADE F",
        "is_action_required": True,
        "anomalies": [{"severity": "CRITICAL", "component": "CPU", "message": "High load"}],
    }
    telemetry = {"system": {}}

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        res = notifier.send_alert(eval_data, telemetry)
        assert res["webhook"] is True
        assert mock_post.called
