# Database

The project uses PostgreSQL as the database.
Any changes to schema has to be added in a new `.sql` file and put in the `migrations` directory.
The migrations script (`bdaybot.data.migrations`) keeps track of the migrations. This is run automatically
whenever the bot is run, and need not be run manually.

## Schema
### Users
```
id: text (discord ID)
birthday: date
user_timezone: text
```
### Guilds
```
id: text (discord ID)
message: text = "Hey everyone, it's {user}'s birthday!"
active: bool
```

### Users-guilds
```
user_id: text, fkey(users.id, on delete cascade)
guild_id: text, fkey(guilds.id, on delete cascade)
active: bool = true
```

### Migrations
The migrations script will maintain a table of migration records:

```
id: int, autoincrement
script_name: text
migr_time: datetime = NOW()
status: enum(success - 1, fail - 0)
query_hash: text
```

Essentially, the migration script will:
- check if there's any new scripts in the migrations folder
- try and run them
- log whether the migration succeeds/fails
- if it is a fail, the hash is used to check if the exact same query was run before
