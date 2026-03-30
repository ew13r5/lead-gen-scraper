# Lead Gen Scraper

B2B lead generation data pipeline. Scrapes company data from public business directories, processes it through a multi-stage cleaning pipeline, and exports clean, deduplicated results.

## Features

- **6 data sources**: YellowPages, Yelp, BBB, Clutch (static), Crunchbase (Playwright)
- **Data pipeline**: HTML cleaning, field validation, fuzzy deduplication, optional enrichment
- **Demo mode**: Faker-generated data with intentional quality issues to demonstrate pipeline
- **Web UI**: React dashboard with AG Grid results table, real-time progress, pipeline visualization
- **Export**: CSV, Excel, JSON, Google Sheets
- **Background processing**: Celery tasks with Redis, WebSocket progress updates
- **Docker**: Single `docker-compose up` for full stack

## Quick Start

```bash
# Clone and start
git clone <repo-url>
cd lead-gen-scraper

# Copy environment config
cp backend/.env.example backend/.env

# Start all services
docker-compose up --build
```

Open `http://localhost:3010` in your browser. In demo mode, 500 sample companies are auto-seeded on first startup.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@leadgen-postgres:5432/leadgen` | PostgreSQL connection |
| `REDIS_URL` | `redis://leadgen-redis:6379/0` | Redis for Celery + WebSocket pub/sub |
| `APP_MODE` | `demo` | `demo` (Faker data) or `live` (real scraping) |
| `EXPORTS_DIR` | `/app/exports` | Directory for CSV/Excel/JSON exports |
| `SOURCES_DIR` | `/app/sources` | YAML source config directory |
| `GOOGLE_SHEETS_CREDENTIALS` | _(empty)_ | Service Account JSON for Google Sheets export |
| `CORS_ORIGINS` | `["http://localhost:3010"]` | Allowed CORS origins |

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tasks/` | Create scrape task |
| GET | `/api/v1/tasks/` | List tasks |
| GET | `/api/v1/tasks/{id}` | Get task details |
| DELETE | `/api/v1/tasks/{id}` | Cancel task |
| GET | `/api/v1/results/` | List scraped companies |
| GET | `/api/v1/results/{id}` | Get company details |
| PATCH | `/api/v1/results/{id}` | Edit company fields |
| POST | `/api/v1/export/` | Export results (CSV/Excel/JSON/Sheets) |
| GET | `/api/v1/export/{id}/download` | Download export file |
| GET | `/api/v1/sources/` | List available sources |
| GET | `/api/v1/pipeline/{task_id}` | Pipeline stage stats |
| GET | `/api/v1/mode/` | Get current mode |
| PUT | `/api/v1/mode/` | Switch mode (live/demo) |
| POST | `/api/v1/demo/seed` | Seed demo data |
| POST | `/api/v1/demo/reset` | Reset demo data |
| GET | `/api/v1/health` | Service health check |
| WS | `/ws/tasks/{id}/progress` | Real-time task progress |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Celery, Redis |
| Frontend | React 18, TypeScript, Tailwind CSS, AG Grid |
| Database | PostgreSQL 15 |
| Scraping | httpx + parsel (static), Playwright (dynamic) |
| Pipeline | Custom stages: HTML cleaner, field validator, deduplicator, enricher |
| Export | CSV, Excel (openpyxl), JSON, Google Sheets (gspread) |
| Deploy | Docker Compose |

## Development

```bash
# Backend (without Docker)
cd backend
uv sync
uv run pytest                    # Run tests
uv run uvicorn main:app --reload # Start API server

# Frontend
cd frontend
npm install
npm run dev                      # Start dev server
npm test                         # Run tests
```

## Project Structure

```
lead-gen-scraper/
  backend/
    api/routes/          # FastAPI endpoints
    scrapers/            # Static + Dynamic scrapers
    pipeline/            # Data processing stages
    tasks/               # Celery background tasks
    sources/             # YAML source configs
    db_models/           # SQLAlchemy models
    demo/                # Faker data seeder
    anti_detection/      # Proxy rotation, stealth
  frontend/
    src/components/      # React UI components
    src/pages/           # Page views
    src/hooks/           # Custom React hooks
    src/api/             # API client
  docker-compose.yml
```
