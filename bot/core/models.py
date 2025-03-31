__all__ = [
    "Settings",
    "Brokage",
    "Message",
    "MessageHandler",
    "DatabaseException",
    "DiscordException",
    "TelegramException",
]

from pathlib import Path
from typing import Callable, Coroutine, Self

import discord
import dotenv
import telegram
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv(), extra="allow"
    )

    discord_bot_token: str = ""
    telegram_bot_token: str = ""

    data_path: Path = Path(__file__).parent.parent.parent / "data"
    db_url: str = f"sqlite:///{data_path/'db.sql'}"


class Brokage(BaseModel):

    subs: dict[int, set[str]] = {}
    """List of publishers (by ID) and their subscribers."""
    pubs: dict[str, int] = {}
    """Dictionary of publishers and their unique IDs."""


class Message(BaseModel):
    """A chat message."""

    chat_id: int
    text: str

    @classmethod
    def from_discord(cls, msg: discord.Message) -> Self:
        """Create a message from a Discord message."""
        return cls(text=msg.content, chat_id=msg.channel.id)

    @classmethod
    def from_telegram(cls, msg: telegram.Message) -> Self:
        """Create a message from a Telegram message."""
        return cls(text=msg.text or "", chat_id=msg.chat_id)


MessageHandler = Callable[[Message], Coroutine[None, None, None]]


class DatabaseException(Exception):
    """An exception raised by the database."""


class DiscordException(Exception):
    """An exception raised by the Discord API."""


class TelegramException(Exception):
    """An exception raised by the Telegram API."""
