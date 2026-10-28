"""Explicit state initialization for the unfinished counting-bot scaffold."""

import argparse
from pathlib import Path
import sqlite3


def create_db(database_path):
    path = Path(database_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS config (group_id INTEGER, channel_name TEXT, actual_number INTEGER)"
        )
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Counting-bot scaffold: initializes state only; no game loop is implemented."
    )
    parser.add_argument(
        "--init-db", type=Path, required=True, help="Explicit path for counting-bot state"
    )
    args = parser.parse_args()
    print(
        f"Counting-bot state initialized at {create_db(args.init_db)}. Gameplay is not implemented."
    )
