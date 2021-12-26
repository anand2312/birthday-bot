"""Module to run the SQL queries in the migrations directory."""
import os
import pathlib
import traceback

import asyncpg
from loguru import logger


MIGRATIONS_PATH = pathlib.Path(__file__).parent / "migrations"


async def create_migrations_table(conn: asyncpg.Connection) -> None:
    q = """CREATE TABLE migrations(
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            script_name TEXT NOT NULL,
            migr_time TIMESTAMP NOT NULL DEFAULT NOW(),
            status INTEGER NOT NULL,
            query_hash TEXT NOT NULL
        )"""
    await conn.execute(q)
    logger.info("Created migrations table ⚒")


async def run_migration(conn: asyncpg.Connection, p: pathlib.Path) -> None:
    """Read a migration file and run it. If successful, log the result."""
    # TODO: THESE SHOULD BE IN FUCKING TRANSACTIONS
    log_query = (
        "INSERT INTO migrations(script_name, status, query_hash) VALUES($1, $2, $3)"
    )
    try:
        await conn.execute(p.read_text())
    except Exception as e:
        await conn.execute(log_query, p.name, 0, hash(p.read_text()))
        logger.exception(f"Couldn't run script: {p.name}")
        traceback.print_tb(e.__traceback__)
    else:
        await conn.execute(log_query, p.name, 1, hash(p.read_text()))
        logger.info(f"Ran migration: {p}")


async def check_if_done(conn: asyncpg.Connection, p: pathlib.Path) -> bool:
    # check if this script has been run succesfully before
    res = await conn.fetchval(
        "SELECT EXISTS(SELECT 1 FROM migrations WHERE script_name = $1 AND status = 1)",
        p.name,
    )
    return True if res else False


async def check_if_same(conn: asyncpg.Connection, p: pathlib.Path) -> bool:
    """Check if the script being run has been run before and resulted in an error."""
    res = await conn.fetchrow(
        "SELECT * FROM migrations WHERE script_name = $1 AND query_hash = $2 AND status = 0",
        p.name,
        hash(p.read_text()),
    )
    return True if res else False


async def run_migrations(conn: asyncpg.Connection) -> None:
    """Entrypoint function."""
    logger.info("Running migrations")
    file_to_status = {}  # dict of file: status
    # status is 1 if it was run, 0 if it wasn't run

    for script in sorted(MIGRATIONS_PATH.glob("*.sql"), key=os.path.getctime):
        done = await check_if_done(conn, script)
        if done:
            logger.info(f"Skipping {script.name} as it's already been run...")
            file_to_status[script] = 1
            continue
        errd = await check_if_same(conn, script)
        if errd:
            logger.warning(
                f"Skipping {script.name} as this script has been run before and resulted in an error. "
                f"Is it a proper query?"
            )
            file_to_status[script] = 0
            continue

        logger.info(f"Running {script.name}...")
        await run_migration(conn, script)
        file_to_status[script] = 1

    latest = max(MIGRATIONS_PATH.glob("*.sql"), key=os.path.getctime)

    if file_to_status[latest] != 1:
        logger.warning(
            f"Database may not be up to date; migration {latest.name} wasn't run"
        )

    logger.info("Migration complete")
