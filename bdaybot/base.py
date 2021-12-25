"""Subclass base Discord models to add extra features."""

from typing import Any

import disnake
from disnake.ext import commands
from loguru import logger


class BirthdayBot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            command_prefix="b!",
            description="Remember your friends' birthdays!",
            intents=disnake.Intents.default(),
            *args,
            **kwargs
        )

    async def on_ready(self) -> None:
        logger.success("Connected to Discord")

        # TODO: add connection to database logic here.
