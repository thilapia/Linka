# Contributing to Linka

## Python setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git. From the repository root:

```sh
uv sync --all-packages --frozen
uv run linka-backend
```

uv downloads the Python version selected by `.python-version` (3.12), creates `.venv`, and installs the workspace members in editable mode. No virtual environment activation or separate pip installation is needed. `uv run linka-backend --host 0.0.0.0 --port 5000` exposes the development server beyond localhost when needed.

Open `http://127.0.0.1:5000/meta` to check the API. The API does not serve a browser frontend at `/`. SQLite databases are initialized automatically. Account creation and sessions work without external service credentials.

The root is a non-packaged project that depends on the Python applications and libraries. All members share one `uv.lock`. Each member declares its own runtime dependencies and can be built independently. See [uv workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) for the dependency model.

## Repository layout

| Path | Component |
| --- | --- |
| `apps/backend/src/linka_backend` | Flask API, its internal signed federation implementation and packaged resources |
| `apps/linka_lite` | Android application; managed with Gradle rather than uv |
| `packages/linka_bots_sdk/src/linka_bots_sdk` | HTTP bot client and explicit credential setup |
| `packages/linka_federations/src/linka_federations` | Public federation SDK |
| `packages/linka_automoderator_bot/src/linka_automoderator_bot` | Backend-started moderation worker, rules and terms |
| `packages/linka_counting_bot/src/linka_counting_bot` | Counting-bot scaffold and explicit state initialization |
| `tests` | Automated Python tests; isolated state and no production requests |
| `docs`, `sites` | Existing Pages client/documentation and static registration pages |

The two SDKs keep their distribution names, `linkabot-sdk` and `linkaFederations`. Import them as `linka_bots_sdk` and `linka_federations`. `LinkaBotSdk` and `LinkaBot` export the same shared client. Instantiate it with an explicit `config_path`; setup no longer happens implicitly. Direct SQLite moderation belongs to AutoModerator, not the HTTP SDK. Historical examples are under package `examples` directories and are not tests.

The public federation SDK and the backend's signed federation helper have different behavior. This migration preserves both rather than changing the federation protocol.

## Configuration and local state

Copy `apps/backend/backend.env.example` to `apps/backend/backend.env` if you need configuration. The file is optional and ignored by Git. Shell environment variables take precedence over file values. Use one environment file for the API and its bridges.

- `LINKA_ENV_FILE`: explicit environment file path. Defaults to `apps/backend/backend.env` in an editable checkout.
- `LINKA_DATA_DIR`: directory holding SQLite files, generated federation keys and default bot configuration. Defaults to `apps/backend/DB` in an editable checkout. For a wheel install, defaults to the OS user data directory returned by `platformdirs.user_data_path("linka", appauthor=False)`; its default environment file is `backend.env` inside that directory.
- `LINKA_CONFIG_FILE`: optional feature configuration JSON, replacing the packaged `backend.json`. Copy `apps/backend/src/linka_backend/backend.json` to an ignored local file and set this variable to customize it. In particular, set `modules-flags.url-server` to your node URL. The migration preserves existing feature defaults and server identity; change that URL for a local node.
- `LINKA_AUTOMOD_CONFIG`: bot credential file. Defaults to `automoderator.json` inside the data directory.

Prefer absolute paths for environment overrides. They resolve relative to the process working directory when supplied as relative paths. The application does not change cwd or search for a checkout named `Linka`.

Media storage is initialized only when used. Set both B2 credential variables to enable uploads and media proxy requests. Mastodon/Bluesky credentials and SMTP credentials are optional and only needed for their respective operations.

## Automatic AutoModerator

The existing `modules-flags.automoderator` flag is enabled by default. The backend starts its daemon thread after application initialization, waits five seconds, then scans every 120 seconds. There is at most one worker per Python process. Multi-worker WSGI deployments need an operational choice of one bot-hosting process; this change does not provide cross-process leader election.

On the first run, absent or invalid bot credentials produce a setup instruction in the log while the API remains available. With the backend running, configure an existing account in another terminal:

```sh
uv run linka-automoderator-setup --config apps/backend/DB/automoderator.json --username AutoModerator
```

The command prompts for a password and validates it against localhost. Add `--register --email you@example.test` to create a new account, or `--url http://your-node:5000` to select another node. It will not overwrite an existing configuration. Credential JSON contains a password; keep it outside version control and restrict local file access.

Restart the backend after setup. For custom data directories, pass the same absolute config path to setup and `LINKA_AUTOMOD_CONFIG` on the backend. A standalone invocation is also available:

```sh
uv run linka-automoderator --config /absolute/path/to/automoderator.json --database /absolute/path/to/post.db
```

Use the local backend URL and that backend's database together: AutoModerator is a privileged local bot that edits its explicitly configured post database. No separate `MASTER_KEY` is required for those local writes. Do not run the standalone worker alongside automatic startup for the same node. Moderation rules, terms, and scan timing are preserved.

The counting bot remains unfinished. `uv run linka-counting-bot --init-db /absolute/path/to/counting.db` initializes its original schema only; it does not start a counting game. Its package is ready for further development using the shared SDK.

## Checks and dependencies

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build --all-packages
```

The tests use temporary directories and fake external transport. Legacy `main_teste.py` is another application entry point; old message-sending examples are not collected as tests.

Ruff initially enforces syntax errors and severe correctness rules (`E9`, `F63`, `F7`, `F82`) repository-wide for Python sources. Formatting covers new tooling, tests, and bot/SDK code; legacy backend modules and the public federation client are explicitly excluded to avoid a repository-wide formatting diff. Android helper scripts, generated web files, and historical examples are excluded. Broader lint cleanup can be a separate contribution.

Add runtime dependencies to the member that imports them, and development tools at the root:

```sh
uv add --package linka-backend some-library
uv add --package linka_automoderator_bot some-library
uv add --dev some-tool
uv lock
uv sync --all-packages --frozen
```

Commit metadata and lockfile changes together. For tools requiring requirements format, generate it with `uv export --all-packages --no-dev --no-emit-workspace --format requirements-txt --output-file requirements.txt`; this exports third-party dependencies, and workspace packages must still be installed separately. Do not maintain a second dependency list by hand.

## Migrating an existing checkout

Stop backend/bot processes and back up local state first. Only tracked sources are relocated. Ignored databases, environment files and bot credentials are not moved automatically.

1. Move your backed-up `backend/DB` contents into `apps/backend/DB`, or set `LINKA_DATA_DIR` to the existing absolute database directory.
2. Copy your old `backend/backend.env` or `.env` values into `apps/backend/backend.env`. Set `LINKA_ENV_FILE` if retaining another location. Include any bridge credentials formerly held in separate `.env` files.
3. Copy your existing bot `config-login.json` into the selected `automoderator.json` path, preserving its `url`, `username` and `password` fields, or run explicit setup.
4. Existing federation nodes should copy their own private/public key pair into `LINKA_DATA_DIR` before startup to preserve node identity. Legacy PEM files and `config-login.json` are retained locally under `apps/backend` during this migration but are no longer version controlled or included in packages. They are never loaded automatically; do not use shared repository keys for a new node. Missing keys are generated in the data directory.
5. Update launchers/WSGI imports to `linka_backend.main:app`, scripts to `uv run linka-backend`, SDK imports to snake_case, and Android paths to `apps/linka_lite`.

## Android development

Open `apps/linka_lite` in Android Studio, or run `./gradlew assembleDebug` there (`.\gradlew.bat assembleDebug` in PowerShell). The output is `apps/linka_lite/app/build/outputs/apk/debug/`.

The checked-in build requests Gradle 9.3.1, AGP 9.1.1, Java daemon toolchain 21 and compile SDK 34. It also runs an ImageMagick `convert` icon task. The existing Android CI installs Java 17 and legacy SDK platforms; reconciling that toolchain is separate from this relocation. On Windows, the system `convert.exe` is not ImageMagick. Android package/application IDs remain unchanged.
