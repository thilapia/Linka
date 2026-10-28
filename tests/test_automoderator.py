import json
import sqlite3
import threading


def test_missing_configuration_does_not_start_or_prompt(tmp_path, caplog):
    from linka_automoderator_bot.runtime import start_background

    assert start_background(tmp_path / "missing.json", tmp_path / "post.db") is None
    assert "linka-automoderator-setup" in caplog.text
    assert not (tmp_path / "post.db").exists()


def test_disabled_runner_has_no_side_effects(tmp_path):
    from linka_automoderator_bot.runtime import start_background

    assert start_background(tmp_path / "missing.json", tmp_path / "post.db", enabled=False) is None
    assert list(tmp_path.iterdir()) == []


def test_runner_starts_automatically_once_per_process(tmp_path, monkeypatch):
    from linka_automoderator_bot import bot, runtime

    config = tmp_path / "bot.json"
    config.write_text(
        json.dumps({"url": "http://localhost:5000", "username": "bot", "password": "local"})
    )
    database = tmp_path / "post.db"
    started = threading.Event()
    release = threading.Event()
    received = []

    def run(config_path, database_path):
        received.append((config_path, database_path))
        started.set()
        release.wait(5)

    monkeypatch.setattr(runtime, "STARTUP_DELAY", 0)
    monkeypatch.setattr(bot, "main", run)
    worker = runtime.start_background(config, database)
    try:
        assert started.wait(3)
        assert runtime.start_background(config, database) is worker
        assert received == [(config, database)]
        assert worker.daemon
    finally:
        release.set()
        worker.join(5)


def test_moderation_writes_only_to_explicit_database(tmp_path):
    from linka_automoderator_bot.bot import moderate_once

    database = tmp_path / "post.db"
    with sqlite3.connect(database) as conn:
        conn.execute("CREATE TABLE posts (id INTEGER, text_post TEXT)")
        conn.execute("INSERT INTO posts VALUES (1, 'heil hitler'), (2, 'hello friends')")

    class Feed:
        def view_posts(self):
            return [
                {"id": 1, "text_post": "heil hitler", "username": "someone"},
                {"id": 2, "text_post": "hello friends", "username": "someone"},
            ]

    moderate_once(Feed(), database)
    with sqlite3.connect(database) as conn:
        rows = conn.execute("SELECT text_post FROM posts ORDER BY id").fetchall()
    assert "Your post was removed" in rows[0][0]
    assert rows[1][0] == "hello friends"


def test_bot_resources_are_available():
    from linka_automoderator_bot import terms_text

    assert terms_text().strip()


def test_invalid_configuration_keeps_worker_stopped(tmp_path, caplog):
    from linka_automoderator_bot.runtime import start_background

    config = tmp_path / "invalid.json"
    config.write_text("not json")
    assert start_background(config, tmp_path / "post.db") is None
    assert "linka-automoderator-setup" in caplog.text
