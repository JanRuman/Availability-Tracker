from __future__ import annotations

import random
import time
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class FetchOptions:
    timeout_s: int = 30
    min_delay_s: float = 0.6
    max_delay_s: float = 1.6
    max_retries: int = 4
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )


class HttpClient:
    def __init__(self, options: FetchOptions | None = None) -> None:
        self.options = options or FetchOptions()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.options.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "sk,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "DNT": "1",
            }
        )

    def get_text(self, url: str) -> str:
        # Polite randomized delay + basic retry/backoff for transient failures.
        last_err: Exception | None = None
        for attempt in range(self.options.max_retries + 1):
            time.sleep(random.uniform(self.options.min_delay_s, self.options.max_delay_s))
            try:
                resp = self.session.get(url, timeout=self.options.timeout_s, headers={"Referer": url})
                if resp.status_code in {429, 500, 502, 503, 504}:
                    raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
                resp.raise_for_status()
                return resp.text
            except Exception as e:  # noqa: BLE001
                last_err = e
                # Exponential backoff with jitter.
                backoff = min(30.0, (2**attempt) + random.random())
                time.sleep(backoff)
        assert last_err is not None
        raise last_err

