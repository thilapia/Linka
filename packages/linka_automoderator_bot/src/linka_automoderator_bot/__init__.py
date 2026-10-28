"""Automatic moderation bot. Importing this package starts no work."""

from importlib.resources import files


def terms_text():
    return files(__package__).joinpath("terms_of_service.txt").read_text(encoding="utf-8")
