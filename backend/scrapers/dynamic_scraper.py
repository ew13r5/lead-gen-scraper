from __future__ import annotations

import html
import json
import logging
import random
import time
from datetime import datetime, timezone
from typing import Callable

import parsel

from anti_detection.proxy_rotator import ProxyRotator
from anti_detection.stealth_config import apply_stealth, get_browser_args, get_context_options
from anti_detection.user_agent_rotator import UserAgentRotator
from cache.html_cache import HtmlCache
from models.raw_data import ProgressInfo, ScrapeResult
from scrapers.base import BaseScraper
from scrapers.config_loader import SourceConfig, ScrollPagination

logger = logging.getLogger(__name__)


class DynamicScraper(BaseScraper):
    """Playwright-based scraper for JavaScript-rendered sites."""

    async def scrape(
        self, config: SourceConfig, query: str, location: str, limit: int
    ) -> ScrapeResult:
        proxy = None
        if self.proxy_rotator:
            proxy = self.proxy_rotator.get_next()
        if config.proxy.required and not proxy:
            return ScrapeResult(
                items=[],
                pages_scraped=0,
                errors=["Proxy required but none available"],
                source=config.name,
                total_time_seconds=0,
            )

        ua_rotator = UserAgentRotator()
        ua_headers = ua_rotator.get_headers()
        user_agent = ua_headers.get("User-Agent", "")

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return ScrapeResult(
                items=[],
                pages_scraped=0,
                errors=["playwright is not installed"],
                source=config.name,
                total_time_seconds=0,
            )

        start_time = time.perf_counter()
        all_items: list[dict] = []
        errors: list[str] = []
        pages_scraped = 0

        async with async_playwright() as pw:
            launch_kwargs: dict = {
                "headless": True,
                "args": get_browser_args(),
            }
            if proxy:
                launch_kwargs["proxy"] = {"server": proxy.url}

            browser = await pw.chromium.launch(**launch_kwargs)
            try:
                context = await browser.new_context(**get_context_options(user_agent))
                page = await context.new_page()
                await apply_stealth(page)

                url = self._build_url(config, query, location)
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    errors.append(f"Navigation failed: {e}")
                    return ScrapeResult(
                        items=[],
                        pages_scraped=0,
                        errors=errors,
                        source=config.name,
                        total_time_seconds=time.perf_counter() - start_time,
                    )

                try:
                    await page.wait_for_selector(config.listing_selector, timeout=15000)
                except Exception:
                    pass  # May not have items yet, scroll may load them

                max_scrolls = config.pagination.max_pages if isinstance(config.pagination, ScrollPagination) else 10
                prev_count = 0
                no_change_count = 0

                for scroll_num in range(max_scrolls):
                    current_count = await page.locator(config.listing_selector).count()

                    if current_count == prev_count:
                        no_change_count += 1
                        if no_change_count >= 3:
                            break
                    else:
                        no_change_count = 0

                    prev_count = current_count
                    pages_scraped = scroll_num + 1

                    if self.on_progress:
                        self.on_progress(ProgressInfo(
                            pages_processed=pages_scraped,
                            pages_total=max_scrolls,
                            items_found=current_count,
                            errors=len(errors),
                            current_page=scroll_num + 1,
                        ))

                    if current_count >= limit:
                        break

                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    delay = self._gaussian_delay(config.rate_limit.delay_range)
                    await page.wait_for_timeout(int(delay * 1000))

                # Extract data
                if config.app_state_selector:
                    all_items = await self._extract_app_state_json(page, config, url)
                if not all_items:
                    all_items = await self._extract_css(page, config, url)

                all_items = all_items[:limit]

                if proxy and self.proxy_rotator:
                    self.proxy_rotator.mark_success(proxy)

                await context.close()
            except Exception as e:
                errors.append(str(e))
                if proxy and self.proxy_rotator:
                    self.proxy_rotator.mark_failure(proxy)
            finally:
                await browser.close()

        return ScrapeResult(
            items=all_items,
            pages_scraped=pages_scraped,
            errors=errors,
            source=config.name,
            total_time_seconds=time.perf_counter() - start_time,
        )

    def _build_url(self, config: SourceConfig, query: str, location: str) -> str:
        url = config.base_url
        if config.search_params:
            params = {}
            for key, template in config.search_params.items():
                params[key] = template.replace("{query}", query).replace("{location}", location)
            from urllib.parse import urlencode
            url = f"{url}?{urlencode(params)}"
        return url

    async def _extract_app_state_json(
        self, page, config: SourceConfig, page_url: str
    ) -> list[dict]:
        try:
            import jmespath
            el = page.locator(config.app_state_selector)
            if await el.count() == 0:
                return []
            raw = await el.inner_text()
            decoded = html.unescape(raw)
            data = json.loads(decoded)

            if config.app_state_jmespath:
                entities = jmespath.search(config.app_state_jmespath, data)
            else:
                entities = data if isinstance(data, list) else []

            if not entities:
                return []

            items = []
            now = datetime.now(timezone.utc).isoformat()
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                item = {
                    "company_name": entity.get("name") or entity.get("identifier", {}).get("value", ""),
                    "website": entity.get("website_url") or entity.get("homepage_url"),
                    "category": entity.get("category_groups_list") or entity.get("categories"),
                    "address": entity.get("location_identifiers", [{}])[0].get("value") if entity.get("location_identifiers") else entity.get("headquarters", ""),
                    "source": config.name,
                    "source_url": page_url,
                    "scraped_at": now,
                }
                if isinstance(item["category"], list):
                    item["category"] = ", ".join(str(c) for c in item["category"])
                if item["company_name"]:
                    items.append(item)
            return items
        except Exception as e:
            logger.warning("app-state JSON extraction failed: %s", e)
            return []

    async def _extract_css(self, page, config: SourceConfig, page_url: str) -> list[dict]:
        html_content = await page.content()
        sel = parsel.Selector(html_content)
        containers = sel.css(config.listing_selector)

        items = []
        now = datetime.now(timezone.utc).isoformat()
        for container in containers:
            item: dict = {}
            for field_name, css_selector in config.selectors.items():
                if css_selector is None:
                    continue
                value = container.css(css_selector).get()
                if value:
                    item[field_name] = value.strip()
            if item.get("company_name") or item.get("name"):
                if "name" in item and "company_name" not in item:
                    item["company_name"] = item.pop("name")
                item["source"] = config.name
                item["source_url"] = page_url
                item["scraped_at"] = now
                items.append(item)
        return items

    @staticmethod
    def _gaussian_delay(delay_range: list[float]) -> float:
        min_d, max_d = delay_range[0], delay_range[1]
        mean = (min_d + max_d) / 2
        sigma = (max_d - min_d) / 4
        delay = random.gauss(mean, sigma)
        return max(min_d, min(max_d, delay))
