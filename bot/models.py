__all__ = ["Settings", "Message", "DiscordException", "TelegramException"]

import uuid
from pathlib import Path
from threading import Lock
from typing import Callable, Coroutine, Self

import discord
import telegram
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

subscriptions_lock = Lock()


class Settings(BaseSettings):
    """Application settings."""

    discord_bot_token: str = ""
    telegram_bot_token: str = ""
    data_path: Path = Path(__file__).parent.parent / "data"


class Subscriptions(BaseModel):
    """The chat connections between bots."""

    path: Path = Field(default=Path(), exclude=True)

    subs: dict[int, set[int]] = {}
    """List of publishers and their subscribers."""
    pubs: dict[int, int] = {}
    """Dictionary of publishers and their unique IDs."""

    def reset_publisher(self, publisher: int) -> None:
        """Create a new chat as a publisher."""
        self.subs = self.load().subs

        self.pubs[publisher] = uuid.uuid4().int
        self.subs[self.pubs[publisher]] = set()
        self.save()

    def get_publisher(self, publisher: int) -> int:
        """Get the unique ID of a chat."""
        self.pubs = self.load().pubs
        if publisher not in self.pubs:
            self.reset_publisher(publisher)
        return self.pubs[publisher]

    def subscribe(self, subscriber: int, publisher: int) -> None:
        """Add a connection between two chats."""
        self.subs = self.load().subs
        if publisher not in self.subs:
            self.subs[publisher] = set()
        self.subs[publisher].add(subscriber)
        self.save()

    def get_subscribers(self, publisher: int) -> set[int]:
        """Get the subscribers for a chat."""
        self.subs = self.load().subs
        return self.subs.get(publisher, set())

    def unsubscribe_all(self, subscriber: int) -> None:
        """Remove all subscriptions of a chat."""
        self.subs = self.load().subs
        for publisher in list(self.subs):
            self.subs[publisher].discard(subscriber)
        self.save()

    def get_subs_count(self, subscriber: int) -> int:
        """Get the number of subscribers for a chat."""
        self.subs = self.load().subs
        return sum(1 for subs in self.subs.values() if subscriber in subs)

    @classmethod
    def load(cls) -> Self:
        """Load connections from a file."""
        cls.file_path().parent.mkdir(parents=True, exist_ok=True)
        if not cls.file_path().exists():
            return cls(path=cls.file_path())

        subscriptions_lock.acquire()
        data = cls.file_path().read_text()
        subscriptions_lock.release()

        subs = cls.model_validate_json(data)
        subs.path = cls.file_path()
        return subs

    def save(self) -> None:
        """Save connections to a file."""
        self.file_path().parent.mkdir(parents=True, exist_ok=True)
        self.file_path().touch(exist_ok=True)

        subscriptions_lock.acquire()
        self.file_path().write_text(self.model_dump_json(indent=2))
        subscriptions_lock.release()

    @staticmethod
    def file_path() -> Path:
        return Settings().data_path / "connections.json"


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


class DiscordException(Exception):
    """An exception raised by the Discord API."""


class TelegramException(Exception):
    """An exception raised by the Telegram API."""
