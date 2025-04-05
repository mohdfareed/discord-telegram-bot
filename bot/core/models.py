__all__ = [
    "Settings",
    "Brokage",
    "Message",
    "DatabaseException",
    "DiscordException",
    "TelegramException",
]

from pathlib import Path

import dotenv
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
    """A chat broker for managing subscriptions."""

    subs: dict[int, set[str]] = {}
    """List of publishers (by ID) and their subscribers."""
    pubs: dict[str, int] = {}
    """Dictionary of publishers and their unique IDs."""


class BotSettings(BaseModel):
    """Settings for the bot."""

    name: str
    """Bot name."""
    is_active: bool = True
    """Whether the bot is active."""


class Message(BaseModel):
    """A chat message."""

    chat_id: int
    text: str


class DatabaseException(Exception):
    """An exception raised by the database."""


class DiscordException(Exception):
    """An exception raised by the Discord API."""


class TelegramException(Exception):
    """An exception raised by the Telegram API."""

    """An exception raised by the Telegram API."""
