CREATE TABLE IF NOT EXISTS public.users(
    id TEXT PRIMARY KEY,
    birthday DATE NOT NULL,
    user_timezone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public.guilds(
    id TEXT PRIMARY KEY,
    wish_message TEXT NOT NULL DEFAULT 'Hey everyone, it''s {user}''s birthday today! Don''t forget to wish them!',
    active BOOLEAN NOT NULL DEFAULT 'true'
);

CREATE TABLE IF NOT EXISTS public.users_guilds(
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    guild_id TEXT REFERENCES guilds(id) ON DELETE CASCADE,
    active BOOLEAN NOT NULL DEFAULT 'true'
);
