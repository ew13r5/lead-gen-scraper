from __future__ import annotations

import sys
from pathlib import Path

import click

from scrapers.config_loader import validate_config

DEFAULT_SOURCES = Path(__file__).resolve().parent.parent / "sources"


@click.command()
@click.option("--source", help="Source name (validates all if omitted)")
@click.option("--sources-dir", type=click.Path(exists=True), help="Custom sources directory")
def validate(source, sources_dir):
    """Validate YAML source configs."""
    sources_path = Path(sources_dir) if sources_dir else DEFAULT_SOURCES
    has_errors = False

    if source:
        sources_to_check = [source]
    else:
        sources_to_check = [f.stem for f in sources_path.glob("*.yaml")]

    for name in sorted(sources_to_check):
        errors = validate_config(name, sources_path)
        if errors:
            click.echo(f"✗ {name}:")
            for e in errors:
                click.echo(f"    {e}")
            has_errors = True
        else:
            click.echo(f"✓ {name}: OK")

    sys.exit(1 if has_errors else 0)
