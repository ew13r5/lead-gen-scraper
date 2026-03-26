import pytest


@pytest.fixture
def valid_company_data():
    """Return a dict with all RawCompanyData fields populated."""
    return {
        "company_name": "Acme Plumbing Services LLC",
        "phone": "(555) 123-4567",
        "email": "info@acmeplumbing.com",
        "website": "https://acmeplumbing.com",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "category": "Plumbing",
        "rating": "4.7",
        "review_count": 142,
        "source": "yellowpages",
        "source_url": "https://www.yellowpages.com/new-york-ny/acme-plumbing",
        "scraped_at": "2026-03-26T14:30:00Z",
    }


@pytest.fixture
def minimal_company_data():
    """Return a dict with only required RawCompanyData fields."""
    return {
        "company_name": "Test Company",
        "source": "test",
        "source_url": "https://example.com/test",
        "scraped_at": "2026-03-26T12:00:00Z",
    }
