"""Process-local background worker lifecycle used by the backend."""

import json
import logging
from pathlib import Path
import threading
import time

STARTUP_DELAY = 5
_thread = None
_lock = threading.Lock()
logger = logging.getLogger(__name__)


def start_background(config_path, database_path, *, enabled=True):
    """Start once per process, or leave the API available with setup guidance."""
    global _thread
    if not enabled:
        return None
    config_path, database_path = Path(config_path), Path(database_path)
    with _lock:
        if _thread is not None and _thread.is_alive():
            return _thread
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if not all(config.get(key) for key in ("url", "username", "password")):
                raise ValueError("url, username and password are required")
        except (OSError, ValueError, AttributeError) as exc:
            logger.warning(
                "AutoModerator is not configured (%s). Run linka-automoderator-setup --config %s, then restart the backend.",
                exc,
                config_path,
            )
            return None

        def run():
            time.sleep(STARTUP_DELAY)
            try:
                from .bot import main

                main(config_path, database_path)
            except Exception:
                logger.exception("AutoModerator stopped unexpectedly")

        _thread = threading.Thread(target=run, name="linka-automoderator", daemon=True)
        _thread.start()
        return _thread
