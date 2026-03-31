# Demo Video Script (2:45)

## [0:00-0:10] Dashboard

"Lead Gen Scraper — a config-driven B2B lead generation framework. Dashboard shows 228 clean companies from the last run, 5 configured sources, and task history."

## [0:10-0:25] Create a new task

"Creating a new task — select YellowPages, search 'plumbers' in 'New York, NY', limit 100, enable enrichment. Start Scraping."

## [0:25-0:50] Real-time progress

"Real-time WebSocket progress — the scraper is fetching pages with auto-pagination. Now the pipeline kicks in: Stage 1 cleaning... Stage 2 validating... Stage 3 deduplicating. 100 scraped, 96 cleaned, 91 validated, 78 unique leads."

## [0:50-1:10] Pipeline visualization

"Pipeline visualization — see exactly what happened at each stage. 22% of records removed: 4 HTML issues, 5 invalid emails, 13 duplicates. Every record accounted for."

## [1:10-1:35] Results table

"AG Grid results — filter by city, sort by rating, search for companies. Phone numbers normalized. Inline editing before export. Let me select 50 leads and export to Excel..."

## [1:35-1:50] Export

"One click — Excel with frozen headers and auto-filters. Also: CSV, JSON, or Google Sheets auto-create."

## [1:50-2:10] YAML config

"The extensibility — this is the YellowPages source config. YAML file with selectors, pagination, rate limits. Each of the 5 sources is a YAML file. Adding a new directory: 15 minutes, zero code."

## [2:10-2:25] Demo mode

"Demo Mode generates intentionally dirty data — duplicates, bad emails, mixed formats — and runs it through the pipeline. See data quality improvement without scraping."

## [2:25-2:45] Closing

"253 tests — 216 backend, 37 frontend. Five Docker containers, one command. Config-driven, pipeline-first. This framework adapts to any B2B directory with a YAML config."
