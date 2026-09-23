"""
Resilient HTTP Client with exponential backoff, rate limiting, and header rotation.
"""

from __future__ import annotations
import random
import time
from typing import Any, Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class RateLimiter:
    """Enforces polite rate limiting with randomized delay jitter to prevent IP throttling."""

    def __init__(self, min_delay: float = 0.5, max_delay: float = 1.5) -> None:
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request_time: float = 0.0

    def wait(self) -> float:
        """Pauses execution if the elapsed time since last call is lower than target interval."""
        now = time.time()
        elapsed = now - self._last_request_time
        target_delay = random.uniform(self.min_delay, self.max_delay)

        if elapsed < target_delay:
            sleep_duration = target_delay - elapsed
            time.sleep(sleep_duration)
        else:
            sleep_duration = 0.0

        self._last_request_time = time.time()
        return sleep_duration


class ResilientHTTPClient:
    """
    Robust HTTP Session manager configured with retry logic, exponential backoff,
    User-Agent pool rotation, and sensible timeout constraints.
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    ]

    def __init__(
        self,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
        timeout: float = 10.0,
        rate_limiter: Optional[RateLimiter] = None,
    ) -> None:
        self.timeout = timeout
        self.rate_limiter = rate_limiter or RateLimiter(min_delay=0.1, max_delay=0.3)
        self.session = requests.Session()

        retry_strategy = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Constructs headers with rotated User-Agent and browser mimics."""
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Performs a rate-limited GET request with retry backing."""
        self.rate_limiter.wait()
        req_headers = self._get_headers(headers)
        return self.session.get(url, params=params, headers=req_headers, timeout=self.timeout)

    def close(self) -> None:
        """Closes the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> ResilientHTTPClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
