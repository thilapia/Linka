"""Explicit credential setup; never called during imports or client construction."""

import argparse
import getpass
import json
from pathlib import Path

import requests


def configure(config_path, url, username, password, *, register=False, email=None):
    path = Path(config_path).expanduser().resolve()
    if path.exists():
        raise FileExistsError(f"Configuration already exists: {path}")
    url = url.rstrip("/")
    payload = {"username": username, "password": password}
    if register:
        if not email:
            raise ValueError("Email is required to register a bot account")
        payload["email"] = email
    response = requests.post(
        url + ("/register" if register else "/login"), json=payload, timeout=10
    )
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump({"url": url, "username": username, "password": password}, output, indent=2)
    path.chmod(0o600)
    return path


def main(argv=None, *, default_config=None):
    parser = argparse.ArgumentParser(description="Configure a Linka bot account explicitly")
    parser.add_argument(
        "--config", type=Path, required=default_config is None, default=default_config
    )
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--username")
    parser.add_argument("--register", action="store_true")
    parser.add_argument("--email")
    args = parser.parse_args(argv)
    username = args.username or input("Bot username: ").strip()
    password = getpass.getpass("Bot password: ")
    try:
        path = configure(
            args.config, args.url, username, password, register=args.register, email=args.email
        )
    except (ValueError, OSError, requests.RequestException) as exc:
        parser.exit(1, f"Setup failed: {exc}\n")
    print(f"Bot configuration saved to {path}")
