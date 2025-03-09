"""The bot package."""

__all__ = ["APP_NAME", "__version__"]

from importlib.metadata import version

APP_NAME = "bot"
__version__ = version("discord-telegram-bot")
