from pydantic import BaseModel


class RawCompanyData(BaseModel):
    """A single scraped company record. Output contract for the scraping engine."""

    company_name: str
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    category: str | None = None
    rating: str | None = None
    review_count: int | None = None
    source: str
    source_url: str
    scraped_at: str


class ScrapeResult(BaseModel):
    """Result of a scrape operation. Contains items and metadata."""

    items: list[dict]
    pages_scraped: int
    pages_skipped: int = 0
    errors: list[str] = []
    source: str
    total_time_seconds: float


class ProgressInfo(BaseModel):
    """Progress update emitted during scraping."""

    pages_processed: int
    pages_total: int | None = None
    items_found: int
    errors: int
    current_page: int
