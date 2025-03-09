__all__ = ["Settings", "Message", "DiscordException", "TelegramException"]

from pathlib import Path

import discord
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    discord_bot_token: str = ""
    telegram_bot_token: str = ""
    data_path: Path = Path(__file__).parent.parent / "data"


class Message(BaseModel):
    """A bot message."""

    text: str

    @classmethod
    def from_discord(cls, msg: discord.Message) -> "Message":
        """Create a message from a Discord message."""
        return cls(text=msg.content)


class DiscordException(Exception):
    """An exception raised by the Discord API."""


class TelegramException(Exception):
    """An exception raised by the Telegram API."""
