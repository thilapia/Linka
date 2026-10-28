"""Standalone commands for explicit bot setup and operation."""

import argparse
import os
from pathlib import Path


def setup():
    from linka_bots_sdk.setup import main

    main(default_config=os.environ.get("LINKA_AUTOMOD_CONFIG"))


def main():
    parser = argparse.ArgumentParser(description="Run AutoModerator against a local Linka database")
    parser.add_argument(
        "--config",
        type=Path,
        default=os.environ.get("LINKA_AUTOMOD_CONFIG"),
        required="LINKA_AUTOMOD_CONFIG" not in os.environ,
    )
    parser.add_argument("--database", type=Path, required=True)
    args = parser.parse_args()
    from .bot import main as run

    run(args.config, args.database)
