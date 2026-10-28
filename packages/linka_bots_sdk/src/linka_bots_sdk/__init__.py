"""Shared Linka bot SDK. No network or filesystem changes on import."""

from .client import LinkaBotSdk

LinkaBot = LinkaBotSdk
__version__ = "0.1.0"
__all__ = ["LinkaBotSdk", "LinkaBot"]
