"""Resolve configuration, resources and writable state without depending on cwd."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from platformdirs import user_data_path

RESOURCE_DIR = Path(__file__).resolve().parent
_source_app = RESOURCE_DIR.parents[1]
APP_DIR = _source_app if (_source_app / "pyproject.toml").is_file() else None
_default_data = APP_DIR / "DB" if APP_DIR else user_data_path("linka", appauthor=False)
ENV_FILE = (
    Path(
        os.environ.get(
            "LINKA_ENV_FILE",
            str(APP_DIR / "backend.env" if APP_DIR else _default_data / "backend.env"),
        )
    )
    .expanduser()
    .resolve()
)
load_dotenv(ENV_FILE, override=False)
DATA_DIR = Path(os.environ.get("LINKA_DATA_DIR", str(_default_data))).expanduser().resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
AUTOMOD_CONFIG = (
    Path(os.environ.get("LINKA_AUTOMOD_CONFIG", str(DATA_DIR / "automoderator.json")))
    .expanduser()
    .resolve()
)


def load_settings():
    """Use an explicit config override or the packaged feature defaults."""
    path = (
        Path(os.environ.get("LINKA_CONFIG_FILE", str(RESOURCE_DIR / "backend.json")))
        .expanduser()
        .resolve()
    )
    with path.open(encoding="utf-8") as config:
        return json.load(config)
