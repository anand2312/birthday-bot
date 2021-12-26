"""Database utility functions"""
import os
import pathlib
from typing import Mapping

from dotenv import load_dotenv


load_dotenv(pathlib.Path(__file__).parent.parent.parent / ".env")


def get_database_credentials() -> Mapping[str, str]:
    """
    Return the connection credentials depending on whether the bot is running
    in production or development.
    """
    production = os.environ.get("PRODUCTION") == "true"
    if production:
        return {"dsn": os.environ["DB_URI"]}
    else:
        return {"user": "bdaybot", "database": "bdaybot", "password": "bdaybot"}
