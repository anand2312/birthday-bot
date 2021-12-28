"""Subclass base Discord models to add extra features."""
from typing import Any, cast

import asyncpg
import disnake
from disnake.ext import commands
from loguru import logger

from bdaybot.constants import TEST_GUILDS
from bdaybot.data.migrations import run_migrations
from bdaybot.data.utils import get_database_credentials


class BirthdayBot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            command_prefix="b!",
            description="Remember your friends' birthdays!",
            intents=disnake.Intents.default(),
            test_guilds=TEST_GUILDS,
            *args,
            **kwargs
        )
        self.db_pool: asyncpg.Pool

    async def on_ready(self) -> None:
        logger.success("Connected to Discord")
        await self._connect_db()
        await self._run_migrations()

    async def _connect_db(self) -> None:
        """Connect to the database if it isn't already connected."""
        logger.info("Connecting to database")
        if hasattr(self, "db_pool"):
            logger.info("Connected to the database already")
            return

        self.db_pool = cast(
            asyncpg.Pool, await asyncpg.create_pool(**get_database_credentials())
        )
        logger.success("Connected to Postgres")

    async def _run_migrations(self) -> None:
        """Run database migrations"""
        async with self.db_pool.acquire() as conn:
            await run_migrations(conn)
