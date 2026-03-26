from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from anti_detection.proxy_rotator import ProxyRotator
from cache.html_cache import HtmlCache
from models.raw_data import ProgressInfo, ScrapeResult
from scrapers.config_loader import SourceConfig


class BaseScraper(ABC):
    def __init__(
        self,
        cache: HtmlCache | None = None,
        proxy_rotator: ProxyRotator | None = None,
        on_progress: Callable[[ProgressInfo], None] | None = None,
    ) -> None:
        self.cache = cache
        self.proxy_rotator = proxy_rotator
        self.on_progress = on_progress

    @abstractmethod
    async def scrape(
        self, config: SourceConfig, query: str, location: str, limit: int
    ) -> ScrapeResult:
        ...

    def scrape_sync(
        self, config: SourceConfig, query: str, location: str, limit: int
    ) -> ScrapeResult:
        import asyncio
        return asyncio.run(self.scrape(config, query, location, limit))
