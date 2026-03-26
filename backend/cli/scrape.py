from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import click

from anti_detection.proxy_rotator import ProxyRotator
from cache.html_cache import HtmlCache
from models.raw_data import ProgressInfo
from scrapers.source_router import SourceRouter

DEFAULT_SOURCES = Path(__file__).resolve().parent.parent / "sources"


@click.command()
@click.option("--source", required=True, help="Source name (e.g., yellowpages)")
@click.option("--query", required=True, help='Search query (e.g., "plumbers")')
@click.option("--location", required=True, help='Location (e.g., "New York, NY")')
@click.option("--limit", default=100, type=int, help="Max results")
@click.option("--cache-dir", type=click.Path(), help="HTML cache directory")
@click.option("--from-cache", is_flag=True, help="Use cached HTML only")
@click.option("--proxy-file", type=click.Path(exists=True), help="Path to proxies.txt")
@click.option("--output", type=click.Path(), help="Output JSON file (default: stdout)")
@click.option("--verbose", is_flag=True, help="Show progress")
def scrape(source, query, location, limit, cache_dir, from_cache, proxy_file, output, verbose):
    """Scrape company data from a business directory."""
    from scrapers.config_loader import validate_config

    errors = validate_config(source, DEFAULT_SOURCES)
    if errors:
        click.echo(f"Config errors for '{source}':", err=True)
        for e in errors:
            click.echo(f"  - {e}", err=True)
        sys.exit(1)

    cache = HtmlCache(Path(cache_dir)) if cache_dir else None
    proxy_rotator = ProxyRotator(Path(proxy_file)) if proxy_file else None

    def on_progress(info: ProgressInfo):
        if verbose:
            total_str = str(info.pages_total) if info.pages_total else "?"
            click.echo(
                f"[Page {info.pages_processed}/{total_str}] "
                f"Items found: {info.items_found} | Errors: {info.errors}",
                err=True,
            )

    router = SourceRouter(DEFAULT_SOURCES, cache=cache, proxy_rotator=proxy_rotator)
    result = asyncio.run(router.scrape(source, query, location, limit, on_progress=on_progress if verbose else None))

    json_output = json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

    if output:
        Path(output).write_text(json_output, encoding="utf-8")
        click.echo(f"Results written to {output}", err=True)
    else:
        click.echo(json_output)

    click.echo(
        f"\nSummary: {len(result.items)} items, "
        f"{result.pages_scraped} pages scraped, "
        f"{result.pages_skipped} skipped, "
        f"{result.total_time_seconds}s",
        err=True,
    )
