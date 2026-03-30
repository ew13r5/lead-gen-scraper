FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv pip install --system -r pyproject.toml || uv pip install --system httpx parsel "pydantic>=2.0" pyyaml click fake-useragent "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg pydantic-settings alembic celery redis openpyxl gspread email-validator phonenumbers rapidfuzz faker numpy psycopg2-binary asgiref jmespath playwright playwright-stealth

RUN playwright install chromium --with-deps

COPY . .

RUN mkdir -p /app/exports
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
