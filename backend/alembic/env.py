from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from db_models import Company, ScrapeTask, PipelineStat, ExportLog  # noqa: F401
from database import Base
from config import Settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

settings = Settings()
db_url = settings.database_url

is_async = "+asyncpg" in db_url or "+aiosqlite" in db_url

if is_async and "+aiosqlite" in db_url:
    sync_url = db_url.replace("+aiosqlite", "")
elif is_async and "+asyncpg" in db_url:
    sync_url = db_url
else:
    sync_url = db_url

config.set_main_option("sqlalchemy.url", sync_url if "+aiosqlite" in db_url else db_url)


def run_migrations_offline() -> None:
    url = sync_url if not is_async or "+aiosqlite" in db_url else db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online_sync() -> None:
    url = sync_url
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        do_run_migrations(connection)
    connectable.dispose()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        {"sqlalchemy.url": db_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    if "+asyncpg" in db_url:
        asyncio.run(run_async_migrations())
    else:
        run_migrations_online_sync()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
