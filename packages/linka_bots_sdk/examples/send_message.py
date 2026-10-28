"""Explicit message example: configure a test account before running."""
import argparse

from linka_bots_sdk import LinkaBotSdk


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--receiver", required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    bot = LinkaBotSdk(config_path=args.config)
    bot.send_chat(args.message, args.receiver)


if __name__ == "__main__":
    main()
