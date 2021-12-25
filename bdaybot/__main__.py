import os
import pathlib

from dotenv import load_dotenv

from bdaybot import bot


load_dotenv(pathlib.Path(__file__).parent.parent / ".env")


bot.run(os.environ.get("TOKEN"))
