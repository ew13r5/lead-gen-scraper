from __future__ import annotations

import asyncio
import ipaddress
import re
from urllib.parse import urlparse

import httpx

from pipeline.base import PipelineStage

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
FILTERED_PREFIXES = ("info@", "support@", "sales@", "webmaster@", "admin@",
                     "noreply@", "no-reply@", "donotreply@", "example@")
FILTERED_DOMAINS = ("googleapis.com", "cloudflare.com", "sentry.io", "example.com")
SOCIAL_PATTERNS = {
    "linkedin": re.compile(r'https?://(?:www\.)?linkedin\.com/company/[^\s"\'<>]+'),
    "facebook": re.compile(r'https?://(?:www\.)?facebook\.com/[^\s"\'<>]+'),
    "twitter": re.compile(r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[^\s"\'<>]+'),
}
CONTACT_PATHS = ("/contact", "/about", "/contact-us")


def _is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname or ""
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_global
        except ValueError:
            return True
    except Exception:
        return False


class Enricher(PipelineStage):
    TIMEOUT = 10
    MAX_CONCURRENCY = 5
    MAX_RESPONSE = 1_048_576

    @property
    def name(self) -> str:
        return "enricher"

    def process(self, data: list[dict]) -> list[dict]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop is None:
            return asyncio.run(self._async_process(data))
        else:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self._async_process(data)).result()

    async def _async_process(self, data: list[dict]) -> list[dict]:
        sem = asyncio.Semaphore(self.MAX_CONCURRENCY)
        stats = {"websites_checked": 0, "websites_alive": 0, "emails_found": 0, "social_links_found": 0}

        async with httpx.AsyncClient(timeout=self.TIMEOUT, follow_redirects=True) as client:
            tasks = [self._enrich_record(record, client, sem, stats) for record in data]
            await asyncio.gather(*tasks)

        self._stats = stats
        return data

    def run(self, data, **kw):
        self._stats = {}
        result_data, stage_result = super().run(data)
        stage_result.details = self._stats
        return result_data, stage_result

    async def _enrich_record(self, record: dict, client: httpx.AsyncClient,
                             sem: asyncio.Semaphore, stats: dict) -> None:
        website = record.get("website")
        if not website or not _is_safe_url(website):
            return

        async with sem:
            stats["websites_checked"] += 1
            alive = await self._check_alive(client, website)
            record["website_alive"] = alive
            if alive:
                stats["websites_alive"] += 1

            if alive and not record.get("email"):
                email = await self._extract_email(client, website)
                if email:
                    record["email"] = email
                    stats["emails_found"] += 1

            if alive:
                social = await self._extract_social(client, website)
                if social:
                    record["social_links"] = social
                    stats["social_links_found"] += 1

    async def _check_alive(self, client: httpx.AsyncClient, url: str) -> bool:
        try:
            resp = await client.head(url)
            if resp.status_code == 405:
                resp = await client.get(url)
            return 200 <= resp.status_code < 300
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPError):
            return False

    async def _extract_email(self, client: httpx.AsyncClient, base_url: str) -> str | None:
        for path in CONTACT_PATHS:
            try:
                resp = await client.get(base_url.rstrip("/") + path)
                if resp.status_code != 200:
                    continue
                text = resp.text[:self.MAX_RESPONSE]
                emails = EMAIL_REGEX.findall(text)
                for email in emails:
                    lower = email.lower()
                    if any(lower.startswith(p) for p in FILTERED_PREFIXES):
                        continue
                    if any(lower.endswith(d) for d in FILTERED_DOMAINS):
                        continue
                    return email
            except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPError):
                continue
        return None

    async def _extract_social(self, client: httpx.AsyncClient, url: str) -> dict | None:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None
            text = resp.text[:self.MAX_RESPONSE]
            links = {}
            for platform, pattern in SOCIAL_PATTERNS.items():
                match = pattern.search(text)
                if match:
                    links[platform] = match.group(0)
            return links if links else None
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPError):
            return None
