# Linka AutoModerator bot

Installable package `linka_automoderator_bot`, sharing the HTTP client from `linkabot-sdk`.

The backend starts the bot automatically through its existing feature flag. Configure credentials explicitly with `uv run linka-automoderator-setup --config apps/backend/DB/automoderator.json --username AutoModerator` while the local backend is running, then restart the backend. Missing credentials leave the API available and log setup guidance.

The worker starts after five seconds and scans every 120 seconds. It needs an explicit local post database for moderation writes. It starts at most once per application process; use one bot-hosting process per node. Standalone setup/run commands are available; see [contributor instructions](../../CONTRIBUTING.md).
