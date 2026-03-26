from __future__ import annotations

import asyncio
from pathlib import Path

import click
import httpx
import parsel

from anti_detection.user_agent_rotator import UserAgentRotator
from scrapers.config_loader import load_source_config

DEFAULT_SOURCES = Path(__file__).resolve().parent.parent / "sources"


@click.command()
@click.option("--source", required=True, help="Source name")
@click.option("--query", required=True, help="Search query")
@click.option("--location", required=True, help="Location")
@click.option("--proxy-file", type=click.Path(exists=True), help="Proxy file")
def test_source(source, query, location, proxy_file):
    """Smoke test: fetch one page and report selector matches."""
    config = load_source_config(source, DEFAULT_SOURCES)
    ua = UserAgentRotator()
    headers = ua.get_headers()

    from scrapers.static_scraper import StaticScraper
    scraper = StaticScraper()
    url = scraper._build_url(config, query, location, 0)

    click.echo(f"Source: {source}")
    click.echo(f"URL: {url}\n")

    try:
        resp = asyncio.run(_fetch(url, headers))
    except Exception as e:
        click.echo(f"Error fetching: {e}", err=True)
        return

    sel = parsel.Selector(resp)

    containers = sel.css(config.listing_selector)
    click.echo(f"Listing selector: {config.listing_selector} -> {len(containers)} matches\n")

    click.echo("Field selectors:")
    for field, css in config.selectors.items():
        matches = sel.css(css).getall()
        status = f"{len(matches)} matches" if matches else "0 matches ⚠"
        click.echo(f"  {field:20s} ({css}) -> {status}")

    if containers:
        click.echo(f"\nSample data (first {min(3, len(containers))} listings):")
        for i, container in enumerate(containers[:3]):
            parts = []
            for field, css in config.selectors.items():
                val = container.css(css).get()
                if val:
                    parts.append(f'{field}: "{val.strip()}"')
            click.echo(f"  {i+1}. {', '.join(parts)}")


async def _fetch(url: str, headers: dict) -> str:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
        return resp.text
