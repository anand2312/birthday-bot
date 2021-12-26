CREATE TABLE users(
    id TEXT PRIMARY KEY,
    birthday DATE NOT NULL,
    user_timezone TEXT NOT NULL
);

CREATE TABLE guilds(
    id TEXT PRIMARY KEY,
    wish_message TEXT NOT NULL DEFAULT 'Hey everyone, it''s {user}''s birthday today! Don''t forget to wish them!',
    active BOOLEAN NOT NULL DEFAULT 'true'
);

CREATE TABLE users_guilds(
    user_id TEXT REFERENCES users.id ON DELETE CASCADE,
    guild_id TEXT REFERENCES guilds.id ON DELETE CASCADE,
    active BOOLEAN NOT NULL DEFAULT 'true'
);
