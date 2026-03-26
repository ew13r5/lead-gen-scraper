import click

from cli.scrape import scrape
from cli.validate import validate
from cli.test_source import test_source


@click.group()
def cli_group():
    """Lead Gen Scraper - B2B data extraction from business directories."""
    pass


cli_group.add_command(scrape)
cli_group.add_command(validate)
cli_group.add_command(test_source, name="test-source")
