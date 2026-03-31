# Case Study: Lead Gen Scraper — Config-Driven B2B Lead Generation

## Challenge

A B2B sales agency was spending 20+ hours per week on manual lead research across multiple directories. The collected data had ~15% duplicate rate, ~10% invalid email addresses, and phone numbers in inconsistent formats — resulting in wasted outreach efforts and low conversion rates. Every new data source required hiring a developer for weeks of custom scraper development.

## Solution

Built Lead Gen Scraper — a config-driven framework where adding a new source means creating a YAML file (~15 minutes), and a 4-stage data pipeline automatically cleans, validates, deduplicates, and enriches every record.

## Technical Approach

**Config-Driven Architecture**: Each source is described by a YAML file containing URL patterns, CSS/XPath selectors, pagination type, and rate limits. A Source Router reads the config and dispatches to the appropriate scraper engine — httpx + parsel for static HTML sites, Playwright + stealth for JavaScript-rendered pages. Adding Clutch.co as a new source took 12 minutes — zero Python code was changed.

**4-Stage Composable Pipeline**: Each stage implements a `process(data) -> data` interface and tracks input/output counts. Stages can be reordered, skipped, or extended. The Deduplicator uses rapidfuzz with a configurable threshold (default 85%) to catch near-duplicates that exact matching misses.

**Anti-Detection**: Proxy rotation with health-tracking quarantine (mark_success / mark_failure), 4 Chrome user-agent profiles with full header sets, Gaussian delay distribution (not uniform — harder to fingerprint), and playwright-stealth for JavaScript-rendered sources.

## Key Numbers

- **Lead research time**: from 20+ hours/week to under 1 hour
- **Data quality**: pipeline removes 15% duplicates + 10% invalid contacts automatically
- **New source setup**: 15 minutes (YAML config) vs 2-3 weeks (custom development)
- **253 automated tests**: 216 backend (pytest) + 37 frontend (vitest)
- **Pipeline visibility**: per-stage statistics show exactly where data was cleaned and how many records removed
- **5 Docker services**: one-command deployment with auto-seeded demo data

## Tech Stack

Python/FastAPI + React/TypeScript + PostgreSQL + Celery + Redis + Playwright + Docker
