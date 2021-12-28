import os
import pathlib

from dotenv import load_dotenv
from loguru import logger

from bdaybot import bot, EXTENSIONS


load_dotenv(pathlib.Path(__file__).parent.parent / ".env")


for ext in EXTENSIONS:
    try:
        bot.load_extension(ext)
    except Exception as e:
        logger.exception(f"Could not load extension: {ext} | {e}")
    else:
        logger.info(f"Loaded {ext} extension succesfully")


bot.run(os.environ.get("TOKEN"))
