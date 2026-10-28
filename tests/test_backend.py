import json
import os
import subprocess
import sys


def test_backend_from_unrelated_cwd_with_isolated_state(tmp_path):
    state = tmp_path / "state"
    script = """
import json
from linka_backend.main import app
client = app.test_client()
meta = client.get('/meta')
assert meta.status_code == 200, meta.data
assert meta.is_json
terms = client.get('/tos')
assert terms.status_code == 200
assert len(terms.data) > 100
registered = client.post('/register', json={'username': 'localdev', 'password': 'test-password', 'email': 'localdev@example.test'})
assert registered.status_code == 200, registered.data
session = client.post('/new-session', json={'username': 'localdev', 'password': 'test-password'})
assert session.status_code == 200, session.data
assert session.json['token']
print('API_SMOKE_OK')
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        stdin=subprocess.DEVNULL,
        env={
            **os.environ,
            "LINKA_DATA_DIR": str(state),
            "LINKA_ENV_FILE": str(tmp_path / "absent.env"),
            "LINKA_AUTOMOD_CONFIG": str(tmp_path / "missing-bot.json"),
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "API_SMOKE_OK" in result.stdout
    assert (state / "login.db").exists()
    assert (state / "profile.db").exists()
    assert not (tmp_path / "DB").exists()


def test_backend_wires_automatic_worker_to_configured_database(tmp_path):
    config = tmp_path / "bot.json"
    config.write_text(
        json.dumps({"url": "http://localhost:5000", "username": "bot", "password": "local"})
    )
    script = """
import os
from pathlib import Path
import threading
from linka_automoderator_bot import bot, runtime
started = threading.Event()
received = []
def run(config_path, database_path):
    received.append((config_path, database_path))
    started.set()
bot.main = run
runtime.STARTUP_DELAY = 0
from linka_backend.main import app
assert started.wait(3), 'backend did not start its configured worker'
assert received == [(Path(os.environ['LINKA_AUTOMOD_CONFIG']), Path(os.environ['LINKA_DATA_DIR']) / 'post.db')]
assert app.test_client().get('/meta').status_code == 200
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=20,
        env={
            **os.environ,
            "LINKA_DATA_DIR": str(tmp_path / "state"),
            "LINKA_AUTOMOD_CONFIG": str(config),
            "LINKA_ENV_FILE": str(tmp_path / "absent.env"),
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_environment_file_configuration_and_shell_precedence(tmp_path):
    env_file = tmp_path / "backend.env"
    config = tmp_path / "node.json"
    config.write_text(json.dumps({"modules-flags": {"automoderator": False}}))
    bot_config = tmp_path / "bot.json"
    env_file.write_text(
        f'LINKA_DATA_DIR="{(tmp_path / "file-state").as_posix()}"\n'
        f'LINKA_CONFIG_FILE="{config.as_posix()}"\n'
        f'LINKA_AUTOMOD_CONFIG="{bot_config.as_posix()}"\n'
    )
    script = """
import os
from pathlib import Path
from linka_backend.paths import DATA_DIR, AUTOMOD_CONFIG, load_settings
assert DATA_DIR == Path(os.environ['EXPECTED_STATE'])
assert AUTOMOD_CONFIG.name == 'bot.json'
assert load_settings()['modules-flags']['automoderator'] is False
"""
    env = {key: value for key, value in os.environ.items() if not key.startswith("LINKA_")}
    env.update(
        LINKA_ENV_FILE=str(env_file),
        LINKA_DATA_DIR=str(tmp_path / "shell-state"),
        EXPECTED_STATE=str(tmp_path / "shell-state"),
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "file-state").exists()
