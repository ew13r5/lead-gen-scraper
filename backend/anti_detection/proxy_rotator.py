from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Proxy:
    host: str
    port: int
    username: str
    password: str
    success_count: int = 0
    error_count: int = 0
    consecutive_errors: int = 0
    disabled_until: float = 0.0

    @property
    def url(self) -> str:
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"


class ProxyRotator:
    def __init__(
        self,
        proxy_file: Path,
        quarantine_seconds: int = 60,
        max_consecutive_errors: int = 3,
    ):
        self._quarantine_seconds = quarantine_seconds
        self._max_consecutive_errors = max_consecutive_errors
        self._proxies: list[Proxy] = []
        self._index = -1
        self._load(proxy_file)

    def _load(self, proxy_file: Path) -> None:
        for line in proxy_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            if len(parts) != 4:
                logger.warning("Skipping malformed proxy line: %s", line)
                continue
            host, port_str, username, password = parts
            try:
                port = int(port_str)
            except ValueError:
                logger.warning("Skipping proxy with invalid port: %s", line)
                continue
            self._proxies.append(Proxy(host=host, port=port, username=username, password=password))

    def get_next(self) -> Proxy | None:
        if not self._proxies:
            return None
        now = time.time()
        checked = 0
        while checked < len(self._proxies):
            self._index = (self._index + 1) % len(self._proxies)
            proxy = self._proxies[self._index]
            if proxy.disabled_until <= now:
                return proxy
            checked += 1
        return None

    def mark_success(self, proxy: Proxy) -> None:
        proxy.success_count += 1
        proxy.consecutive_errors = 0

    def mark_failure(self, proxy: Proxy) -> None:
        proxy.error_count += 1
        proxy.consecutive_errors += 1
        if proxy.consecutive_errors >= self._max_consecutive_errors:
            proxy.disabled_until = time.time() + self._quarantine_seconds

    @property
    def healthy_count(self) -> int:
        now = time.time()
        return sum(1 for p in self._proxies if p.disabled_until <= now)
