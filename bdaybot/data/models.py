"""Abstraction layer on top of the database."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Type

import arrow
from asyncpg import Connection
from loguru import logger


@dataclass
class Guild:
    """
    Represents a guild's data stored in the database.

    Note: The `users` gield will be None, unless `Guild.fetch_users` is called.
    """

    id: int
    active: bool
    wish_message: str = (
        "Hey everyone, it's {user}'s birthday today! Don't forget to wish them!"
    )
    users: Optional[List[User]] = None

    @classmethod
    async def from_id(cls: Type[Guild], conn: Connection, id: int) -> Guild:
        """Retrieve a guild's info by it's ID."""
        logger.debug(f"Retrieving guild with ID {id}")
        res = await conn.fetchrow("SELECT * FROM guilds WHERE id = $1", str(id))

        if not res:
            raise ValueError(f"Guild with ID {id} does not exist in the database.")

        return cls(id=res["id"], wish_message=res["wish_message"], active=res["active"])

    async def fetch_users(self, conn: Connection) -> List[User]:
        """Fetches the list of users in this guild."""
        logger.debug(f"Fetching users for guild {self.id}")
        res = await conn.fetch(
            "SELECT t1.id, t1.birthday "
            "FROM users t1 JOIN users_guilds t2 "
            "ON t1.id = t2.user_id "
            "WHERE t2.guild_id = $1",
            str(self.id),
        )
        self.users = [User(id=i[0], birthday=i[1]) for i in res]
        return self.users

    async def save(self, conn: Connection) -> None:
        """Saves this guild's information to the `guilds` table. If it already exists, update it."""
        logger.debug(f"Saving guild: {self}")
        await conn.execute(
            "INSERT INTO guilds(id, active) VALUES($1, $2) "
            "ON CONFLICT (id) DO "
            "UPDATE guilds SET wish_message = $3, active = $2 WHERE id = $1",
            str(self.id),
            self.active,
            self.wish_message,
        )

    async def save_user(self, conn: Connection, *, id: int) -> None:
        """Adds the specified user to this guild"""
        logger.debug(f"Saving user {id} to guild {self}")
        await conn.execute(
            "INSERT INTO users_guilds(user_id, guild_id) VALUES($1, $2)",
            str(id),
            str(self.id),
        )


@dataclass
class User:
    """
    Represents a user's data stored in the database.

    Note: The `guilds` field will be None, unless `User.fetch_guilds` is called.
    """

    id: int
    birthday: arrow.Arrow
    guilds: Optional[List[Guild]] = None

    @classmethod
    async def from_id(cls: Type[User], conn: Connection, id: int) -> User:
        """Retrieve a user's info by their ID."""
        logger.debug(f"Retrieving user with ID {id}")
        res = await conn.fetchrow("SELECT * FROM users WHERE id = $1", str(id))

        if not res:
            raise ValueError(f"User with ID {id} does not exist in the database.")

        return cls(id=id, birthday=arrow.get(res["birthday"]))

    async def fetch_guilds(self, conn: Connection) -> List[Guild]:
        """Fetches the list of guilds this user is a part of."""
        logger.debug(f"Mass fetching guilds of user {self.id}")
        res = await conn.fetch(
            "SELECT t1.id, t1.wish_message, t1.active "
            "FROM guilds t1 JOIN users_guilds t2 "
            "ON t1.id = t2.guild_id "
            "WHERE t2.user_id = $1",
            str(self.id),
        )

        self.guilds = [Guild(id=i[0], wish_message=i[1], active=i[2]) for i in res]
        return self.guilds

    async def save(self, conn: Connection) -> None:
        """Saves this user's information to the `users` table. If it already exists, updates it."""
        logger.debug(f"Saving user: {self}")
        await conn.execute(
            "INSERT INTO users(id, birthday) VALUES($1, $2) "
            "ON CONFLICT (id) DO "
            "UPDATE users SET birthday = $2 WHERE id = $1",
            str(self.id),
            self.birthday.datetime,  # arrow to datetime which asyncpg supports
        )
