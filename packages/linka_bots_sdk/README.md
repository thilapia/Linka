# Linka bot SDK

Distribution: `linkabot-sdk`. Import: `linka_bots_sdk`. Requires Python 3.12+.

From the workspace root:

```sh
uv sync --all-packages --frozen
uv run linka-bot-setup --config /absolute/path/to/bot.json --username your-bot
```

Setup explicitly validates credentials against localhost (override with `--url`). Add `--register --email you@example.test` to create an account. It prompts for the password and never overwrites an existing file. Keep credential files private and outside version control.

```python
from linka_bots_sdk import LinkaBotSdk

bot = LinkaBotSdk(config_path="/absolute/path/to/bot.json")
posts = bot.view_posts()
bot.send_chat("hello", "a-local-user")
```

The client offers `view_posts`, `view_friends`, `send_chat`, `get_last_message`, and `comment`. Authentication is lazy. `LinkaBot` is an alias for `LinkaBotSdk`. Importing or constructing a client never prompts or performs authentication. Methods are synchronous; this package does not implement an async bot loop.

Moderation database writes belong to `linka_automoderator_bot`; the shared SDK only talks HTTP. Historical legacy client code lives in `examples/legacy_client.py` for reference.

See [contributor instructions](../../CONTRIBUTING.md) for the shared workspace, dependency updates and tests.
