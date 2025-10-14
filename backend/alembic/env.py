from __future__ import with_statement
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

import sys
import os

# Add the parent directory (backend/) to sys.path before importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import get_settings
from app.db.base import *  # noqa: F401,F403
from app.db.base_class import Base

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.POSTGRES_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)  # Uncommented to enable logging

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=settings.POSTGRES_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    async with connectable.connect() as connection:
        await connection.run_sync(lambda conn: context.configure(connection=conn, target_metadata=target_metadata, compare_type=True))
        await connection.run_sync(lambda _: context.begin_transaction())
        await connection.run_sync(lambda _: context.run_migrations())

def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        import asyncio
        asyncio.run(run_migrations_online())

run()