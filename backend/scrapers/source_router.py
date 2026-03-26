from __future__ import annotations

from pathlib import Path
from typing import Callable

from anti_detection.proxy_rotator import ProxyRotator
from cache.html_cache import HtmlCache
from models.raw_data import ProgressInfo, ScrapeResult
from scrapers.config_loader import SourceConfig, load_all_configs, load_source_config
from scrapers.static_scraper import StaticScraper


class SourceRouter:
    def __init__(
        self,
        sources_dir: Path,
        cache: HtmlCache | None = None,
        proxy_rotator: ProxyRotator | None = None,
    ) -> None:
        self._sources_dir = sources_dir
        self._cache = cache
        self._proxy_rotator = proxy_rotator

    def list_sources(self) -> list[str]:
        return [f.stem for f in self._sources_dir.glob("*.yaml")]

    def get_config(self, source_name: str) -> SourceConfig:
        return load_source_config(source_name, self._sources_dir)

    async def scrape(
        self,
        source_name: str,
        query: str,
        location: str,
        limit: int,
        on_progress: Callable[[ProgressInfo], None] | None = None,
    ) -> ScrapeResult:
        config = self.get_config(source_name)

        if config.renderer == "playwright":
            raise NotImplementedError("Playwright renderer is planned for Phase 2")

        scraper = StaticScraper(
            cache=self._cache,
            proxy_rotator=self._proxy_rotator,
            on_progress=on_progress,
        )
        return await scraper.scrape(config, query, location, limit)
