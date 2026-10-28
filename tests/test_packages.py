import os
from pathlib import Path
import subprocess
import sys


def test_imports_are_installed_and_have_no_startup_side_effects(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import linka_bots_sdk, linka_federations, linka_automoderator_bot, linka_counting_bot",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
        env={**os.environ, "HOME": str(tmp_path), "USERPROFILE": str(tmp_path)},
        stdin=subprocess.DEVNULL,
    )
    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []


def test_client_requires_explicit_configuration_without_prompting(tmp_path):
    import pytest
    from linka_bots_sdk import LinkaBotSdk

    with pytest.raises(FileNotFoundError):
        LinkaBotSdk(config_path=tmp_path / "missing.json")


def test_client_does_not_authenticate_until_needed(tmp_path, monkeypatch):
    import json
    import requests
    from linka_bots_sdk import LinkaBotSdk

    def no_network(*args, **kwargs):
        raise AssertionError("client construction must not contact the server")

    monkeypatch.setattr(requests, "post", no_network)
    config = tmp_path / "bot.json"
    config.write_text(
        json.dumps({"url": "http://localhost:5000/", "username": "bot", "password": "local"})
    )
    client = LinkaBotSdk(config_path=config)
    assert client.url == "http://localhost:5000"
    assert client.name == "bot"


def test_federation_cache_uses_explicit_path(tmp_path):
    from linka_federations import LinkaFederations

    cache = tmp_path / "cache.db"
    fed = LinkaFederations(db_path=cache)
    assert fed.resolve_target("http://localhost:5000") == "http://localhost:5000"
    assert cache.exists()


def test_counting_state_is_initialized_only_by_explicit_command(tmp_path):
    import sqlite3

    database = tmp_path / "nested" / "counting.db"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from linka_counting_bot.bot import main; main()",
            "--init-db",
            str(database),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    with sqlite3.connect(database) as conn:
        assert (
            conn.execute("SELECT group_id, channel_name, actual_number FROM config").fetchall()
            == []
        )
    assert "Gameplay is not implemented" in result.stdout


def test_chat_authenticates_lazily_and_sends_session_token(tmp_path, monkeypatch):
    import json
    import requests
    from linka_bots_sdk import LinkaBotSdk

    config = tmp_path / "bot.json"
    config.write_text(
        json.dumps({"url": "http://localhost:5000", "username": "bot", "password": "local"})
    )
    calls = []

    class Response:
        status_code = 200

        def json(self):
            return {"token": "test-session"}

    def post(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(requests, "post", post)
    client = LinkaBotSdk(config)
    assert calls == []
    assert client.send_chat("hello", "friend")
    assert calls == [
        (
            "http://localhost:5000/new-session",
            {"json": {"username": "bot", "password": "local"}, "timeout": 10},
        ),
        (
            "http://localhost:5000/send-message",
            {
                "json": {"sender": "bot", "receiver": "friend", "message": "hello"},
                "headers": {"Authorization": "Bearer test-session"},
                "timeout": 10,
            },
        ),
    ]
