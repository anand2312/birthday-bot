import time
import traceback
from typing import List

from disnake import ApplicationCommandInteraction
from disnake.embeds import Embed
from disnake.ext import commands
from loguru import logger

from bdaybot import EXTENSIONS
from bdaybot.base import BirthdayBot
from bdaybot.constants import Colour


async def autocomplete_ext(_: ApplicationCommandInteraction, string: str) -> List[str]:
    return [ext for ext in EXTENSIONS if string.lower() in ext.lower()]


class OwnerOnlyCommands(commands.Cog):
    """Commands restriced to bot owners (used for development purposes)."""

    def __init__(self, bot: BirthdayBot) -> None:
        self.bot = bot

    async def cog_slash_command_check(
        self, inter: ApplicationCommandInteraction
    ) -> bool:
        return await self.bot.is_owner(inter.author)

    async def cog_slash_command_error(
        self, inter: ApplicationCommandInteraction, error: Exception
    ) -> None:
        # error = getattr(error, "original", error)
        tb = "\n".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        embed = Embed(
            colour=Colour.RED.value,
            title="An error occurred.",
            description=f"```\n{tb}```",
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command()
    async def unload(
        self,
        inter: ApplicationCommandInteraction,
        ext: str = commands.Param(autocomplete=autocomplete_ext),
    ) -> None:
        """Unload an extension from the bot."""
        logger.info(f"Unloading extension: {ext}")
        self.bot.unload_extension(ext)
        embed = Embed(
            colour=Colour.YELLOW.value,
            title="Extension Unloaded",
            description=f"📤 Extension `{ext}` unloaded.",
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command()
    async def load(
        self,
        inter: ApplicationCommandInteraction,
        ext: str = commands.Param(autocomplete=autocomplete_ext),
    ) -> None:
        """Load an extension to the bot."""
        logger.info(f"Loading extension: {ext}")
        self.bot.load_extension(ext)
        embed = Embed(
            colour=Colour.GREEN.value,
            title="Extension loaded",
            description=f"📥 Extension `{ext}` loaded.",
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command()
    async def reload(
        self,
        inter: ApplicationCommandInteraction,
        ext: str = commands.Param(autocomplete=autocomplete_ext),
    ) -> None:
        """Reload an extension."""
        logger.info(f"Reloading extension: {ext}")
        self.bot.reload_extension(ext)
        embed = Embed(
            colour=Colour.GREEN.value,
            title="Extension reloaded",
            description=f"📥 Extension `{ext}` reloaded.",
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command()
    async def status(self, inter: ApplicationCommandInteraction) -> None:
        """Get general status info from the bot."""
        ws_latency = f"{self.bot.latency * 1000} ms"

        start_db = time.perf_counter_ns()
        await self.bot.db_pool.execute("SELECT 1 FROM users")
        end_db = time.perf_counter_ns()
        db_latency = f"{(end_db - start_db) / 10 ** 6} ms"

        exts = "\n".join([f"• {ext}\n" for ext in self.bot.extensions])

        desc = (
            f"WS Latency: {ws_latency}\n\n"
            f"Database Latency: {db_latency}\n\n"
            f"Loaded Extensions:\n{exts}"
        )

        embed = Embed(
            colour=Colour.BABY_PINK.value, title="BirthdayBot Status", description=desc
        )

        await inter.response.send_message(embed=embed, ephemeral=True)


def setup(bot: BirthdayBot) -> None:
    bot.add_cog(OwnerOnlyCommands(bot))
