from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus, urlencode, urljoin

import httpx
import parsel

from models.raw_data import ProgressInfo, ScrapeResult
from scrapers.base import BaseScraper
from scrapers.config_loader import OffsetPagination, SourceConfig, UrlParamPagination

logger = logging.getLogger(__name__)


class StaticScraper(BaseScraper):
    async def scrape(
        self, config: SourceConfig, query: str, location: str, limit: int
    ) -> ScrapeResult:
        start_time = time.time()
        items: list[dict] = []
        errors: list[str] = []
        pages_scraped = 0
        pages_skipped = 0

        max_pages = config.pagination.max_pages
        sem = asyncio.Semaphore(config.rate_limit.concurrent)

        headers = {}
        if self.proxy_rotator:
            from anti_detection.user_agent_rotator import UserAgentRotator
            ua = UserAgentRotator()
            headers = ua.get_headers()

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            headers=headers,
        ) as client:
            for page_num in range(max_pages):
                if len(items) >= limit:
                    break

                url = self._build_url(config, query, location, page_num)

                async with sem:
                    html = await self._fetch_page(
                        client, config, url, query, location, page_num, errors
                    )

                if html is None:
                    pages_skipped += 1
                    continue

                page_items = self._extract_items(config, html, url)
                items.extend(page_items)
                pages_scraped += 1

                if self.on_progress:
                    self.on_progress(ProgressInfo(
                        pages_processed=pages_scraped,
                        pages_total=max_pages if max_pages < 100 else None,
                        items_found=len(items),
                        errors=len(errors),
                        current_page=page_num + 1,
                    ))

                if not page_items:
                    break

                if page_num < max_pages - 1 and len(items) < limit:
                    delay = self._gaussian_delay(config.rate_limit.delay_range)
                    await asyncio.sleep(delay)

        return ScrapeResult(
            items=items[:limit],
            pages_scraped=pages_scraped,
            pages_skipped=pages_skipped,
            errors=errors,
            source=config.name,
            total_time_seconds=round(time.time() - start_time, 2),
        )

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        config: SourceConfig,
        url: str,
        query: str,
        location: str,
        page_num: int,
        errors: list[str],
    ) -> str | None:
        # Try cache first
        if self.cache:
            cached = self.cache.get(config.name, query, location, page_num)
            if cached is not None:
                return cached

        proxy = self.proxy_rotator.get_next() if self.proxy_rotator else None
        max_retries = config.rate_limit.max_retries

        # Tier 1: retry with same proxy
        for attempt in range(max_retries):
            try:
                proxy_url = proxy.url if proxy else None
                resp = await client.get(url, extensions={"proxy": proxy_url} if proxy_url else {})
                if 200 <= resp.status_code < 300:
                    html = resp.text
                    if self.cache:
                        self.cache.put(config.name, query, location, page_num, html)
                    if proxy and self.proxy_rotator:
                        self.proxy_rotator.mark_success(proxy)
                    return html
                if resp.status_code in (403, 429) or resp.status_code >= 500:
                    backoff = min(2 ** attempt + random.uniform(0, 1), 30)
                    await asyncio.sleep(backoff)
                    continue
                errors.append(f"Page {page_num}: HTTP {resp.status_code} from {url}")
                return None
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                backoff = min(2 ** attempt + random.uniform(0, 1), 30)
                await asyncio.sleep(backoff)

        # Tier 2: rotate proxy
        if self.proxy_rotator and proxy:
            self.proxy_rotator.mark_failure(proxy)
            new_proxy = self.proxy_rotator.get_next()
            if new_proxy and new_proxy != proxy:
                for attempt in range(max_retries):
                    try:
                        resp = await client.get(url, extensions={"proxy": new_proxy.url})
                        if 200 <= resp.status_code < 300:
                            self.proxy_rotator.mark_success(new_proxy)
                            html = resp.text
                            if self.cache:
                                self.cache.put(config.name, query, location, page_num, html)
                            return html
                        backoff = min(2 ** attempt + random.uniform(0, 1), 30)
                        await asyncio.sleep(backoff)
                    except (httpx.TimeoutException, httpx.ConnectError):
                        backoff = min(2 ** attempt + random.uniform(0, 1), 30)
                        await asyncio.sleep(backoff)

        errors.append(f"Page {page_num}: All retries exhausted for {url}")
        return None

    def _extract_items(self, config: SourceConfig, html: str, page_url: str) -> list[dict]:
        sel = parsel.Selector(html)
        containers = sel.css(config.listing_selector)
        items = []

        json_ld_data = {}
        if config.json_ld:
            json_ld_data = self._extract_json_ld(sel, config)

        for i, container in enumerate(containers):
            item: dict = {}
            for field_name, css_selector in config.selectors.items():
                value = container.css(css_selector).get()
                if value:
                    item[field_name] = value.strip()

            # Merge JSON-LD data (overrides CSS)
            if json_ld_data and i < len(json_ld_data):
                for key, val in json_ld_data[i].items():
                    if val:
                        item[key] = val

            if item.get("company_name") or item.get("name"):
                if "name" in item and "company_name" not in item:
                    item["company_name"] = item.pop("name")
                item["source"] = config.name
                item["source_url"] = page_url
                item["scraped_at"] = datetime.now(timezone.utc).isoformat()
                items.append(item)

        return items

    def _extract_json_ld(self, sel: parsel.Selector, config: SourceConfig) -> list[dict]:
        results = []
        scripts = sel.css(config.json_ld.selector)
        for script in scripts:
            text = script.css("::text").get()
            if not text:
                continue
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    for obj in data:
                        results.append(self._map_json_ld(obj, config.json_ld.fields_map))
                elif isinstance(data, dict):
                    results.append(self._map_json_ld(data, config.json_ld.fields_map))
            except json.JSONDecodeError:
                continue
        return results

    @staticmethod
    def _map_json_ld(obj: dict, fields_map: dict[str, str]) -> dict:
        mapped = {}
        for json_path, field_name in fields_map.items():
            value = obj
            for key in json_path.split("."):
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    value = None
                    break
            if value is not None:
                mapped[field_name] = str(value)
        return mapped

    def _build_url(self, config: SourceConfig, query: str, location: str, page_num: int) -> str:
        if config.url_template:
            return config.url_template.format(
                category=quote_plus(query),
                page=self._get_page_value(config, page_num),
                query=quote_plus(query),
                location=quote_plus(location),
            )

        params = {}
        for key, template in config.search_params.items():
            params[key] = template.replace("{query}", query).replace("{location}", location)

        pag = config.pagination
        if isinstance(pag, UrlParamPagination):
            params[pag.param] = str(pag.start + page_num)
        elif isinstance(pag, OffsetPagination):
            params[pag.param] = str(pag.start + page_num * pag.step)

        return f"{config.base_url}?{urlencode(params)}"

    @staticmethod
    def _get_page_value(config: SourceConfig, page_num: int) -> int:
        pag = config.pagination
        if isinstance(pag, UrlParamPagination):
            return pag.start + page_num
        elif isinstance(pag, OffsetPagination):
            return pag.start + page_num * pag.step
        return page_num

    @staticmethod
    def _gaussian_delay(delay_range: list[float]) -> float:
        mean = (delay_range[0] + delay_range[1]) / 2
        stddev = (delay_range[1] - delay_range[0]) / 4
        return max(0, random.gauss(mean, stddev))
