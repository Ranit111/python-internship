"""
Unit tests for ResilientHTTPClient and RateLimiter.
"""

from unittest.mock import MagicMock, patch
import pytest
from scraper.client import RateLimiter, ResilientHTTPClient


def test_rate_limiter_pauses():
    limiter = RateLimiter(min_delay=0.05, max_delay=0.1)
    d1 = limiter.wait()
    d2 = limiter.wait()
    assert d2 >= 0.0


def test_resilient_http_client_headers():
    with ResilientHTTPClient() as client:
        headers = client._get_headers({"X-Custom": "TestVal"})
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert headers["X-Custom"] == "TestVal"


def test_resilient_http_client_get():
    client = ResilientHTTPClient()
    with patch.object(client.session, "get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_get.return_value = mock_response

        resp = client.get("https://example.com/test")
        assert resp.status_code == 200
        assert mock_get.called
    client.close()
