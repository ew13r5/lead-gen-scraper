import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from click.testing import CliRunner

from cli import cli_group
from models.raw_data import ScrapeResult


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_result():
    return ScrapeResult(
        items=[{"company_name": "Test Co", "source": "test", "source_url": "http://test", "scraped_at": "2026-01-01"}],
        pages_scraped=1,
        pages_skipped=0,
        errors=[],
        source="yellowpages",
        total_time_seconds=1.5,
    )


class TestScrapeCommand:
    def test_missing_source_exits_error(self, runner):
        result = runner.invoke(cli_group, ["scrape", "--query", "test", "--location", "NY"])
        assert result.exit_code != 0

    def test_valid_args_runs(self, runner, mock_result):
        with patch("cli.scrape.SourceRouter") as MockRouter:
            instance = MockRouter.return_value
            instance.scrape = AsyncMock(return_value=mock_result)
            result = runner.invoke(cli_group, [
                "scrape", "--source", "yellowpages", "--query", "plumbers", "--location", "NY"
            ])
            assert result.exit_code == 0
            data = json.loads(result.output.split("\n\nSummary")[0])
            assert "items" in data

    def test_output_to_file(self, runner, mock_result, tmp_path):
        out_file = str(tmp_path / "output.json")
        with patch("cli.scrape.SourceRouter") as MockRouter:
            instance = MockRouter.return_value
            instance.scrape = AsyncMock(return_value=mock_result)
            result = runner.invoke(cli_group, [
                "scrape", "--source", "yellowpages", "--query", "test",
                "--location", "NY", "--output", out_file
            ])
            assert result.exit_code == 0
            assert (tmp_path / "output.json").exists()


class TestValidateCommand:
    def test_valid_config_exits_0(self, runner):
        result = runner.invoke(cli_group, ["validate"])
        assert result.exit_code == 0
        assert "yellowpages" in result.output

    def test_all_sources_shown(self, runner):
        result = runner.invoke(cli_group, ["validate"])
        assert "yellowpages" in result.output
        assert "yelp" in result.output
        assert "bbb" in result.output
        assert "clutch" in result.output
