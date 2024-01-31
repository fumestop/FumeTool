`config.py`:

```python
token = "token"

embed_color = 0xE44C65

webhook_id = 12345
webhook_token = "webhook_token"

ipc_secret_key = "ipc_secret_key"
ipc_standard_port = 10003
ipc_multicast_port = 20003

community_server_id = 12345
log_channel_id = 12345

db_name = "db_name"
db_user = "db_user"
db_password = "db_password"
db_host = "localhost"
db_port = 3306

steam_api_key = "steam_api_key"
weather_api_key = "weather_api_key"

topgg_token = "topgg_token"

initial_extensions = [
    "cogs.__dev__",
    "cogs.__error__",
    "cogs.__eval__",
    "cogs.__ipc__",
    "cogs.__topgg__",
    "cogs.development",
    "cogs.fun",
    "cogs.general",
    "cogs.help",
    "cogs.tags",
    "cogs.utility",
]
```

`data/user_blacklist.json`: `[]`

`data/guild_blacklist.json`: `[]`
