"""
Run the SQL files under backend/sql/ against the configured database.

We invoke this from the FastAPI startup hook so the database is always
brought up to the expected schema regardless of how the container was
started (entrypoint.sh, raw uvicorn, etc).

Order is fixed:
    1) schema.sql -> tables, enums (no FKs)
    2) seed.sql   -> bootstrap rows
    3) alter.sql  -> FKs + indexes

All three files are idempotent.
"""

from __future__ import annotations

from pathlib import Path

import asyncpg

from app.config import settings
from app.core.logger import logger


SQL_DIR = Path(__file__).resolve().parent.parent.parent / "sql"

# Order matters - see module docstring.
SQL_FILES: tuple[str, ...] = ("schema.sql", "seed.sql", "alter.sql")


def _asyncpg_dsn(use_default_db: bool = False) -> str:
    """
    Return a DSN for asyncpg.
    If use_default_db is True, replace the database name with 'postgres'.
    """
    dsn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    if use_default_db:
        # Replace whatever database name with 'postgres'
        if "/" in dsn:
            parts = dsn.rsplit("/", 1)
            dsn = parts[0] + "/postgres"
        else:
            dsn += "/postgres"
    return dsn


async def _ensure_database_exists() -> None:
    """
    Connect to the default 'postgres' database and create the target database
    if it does not already exist.
    """
    target_db = settings.DATABASE_URL.split("/")[-1].split("?")[0]
    # Connect to the 'postgres' database
    conn = await asyncpg.connect(_asyncpg_dsn(use_default_db=True))
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", target_db
        )
        if not exists:
            logger.info(f"Database '{target_db}' not found. Creating...")
            # Terminate any connections that might be using the target database
            # (should be none, but safe)
            await conn.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{target_db}' AND pid <> pg_backend_pid()
            """)
            await conn.execute(f"CREATE DATABASE {target_db}")
            logger.info(f"Database '{target_db}' created successfully.")
    finally:
        await conn.close()


async def _run_file(conn: asyncpg.Connection, filename: str) -> None:
    path = SQL_DIR / filename
    if not path.exists():
        logger.warning(f"SQL file not found, skipping: {path}")
        return

    sql = path.read_text(encoding="utf-8")
    if not sql.strip():
        return

    # asyncpg.Connection.execute() uses the simple-query protocol, which
    # accepts whole multi-command scripts (including DO $$ ... $$ blocks).
    await conn.execute(sql)
    logger.info(f"Applied {filename}")


async def run_migrations() -> None:
    # Ensure the target database exists before connecting to it
    await _ensure_database_exists()

    # Now connect to the actual target database (the one from DATABASE_URL)
    conn = await asyncpg.connect(_asyncpg_dsn(use_default_db=False))
    try:
        for fname in SQL_FILES:
            await _run_file(conn, fname)
    finally:
        await conn.close()