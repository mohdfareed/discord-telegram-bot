__all__ = ["ChatBot"]

import asyncio
import logging
from abc import abstractmethod
from typing import Any, Self

from . import broker, db, models


class ChatBot:
    """Chat bot that connects to a chat brokage service."""

    def __init__(self, broker: broker.ChatBroker, db: db.Database) -> None:
        self.logger = logging.getLogger(type(self).__name__)
        self.subscribers: list[ChatBot] = []

        self.broker = broker
        self.database = db
        self.settings = models.BotSettings(name=Self.__name__)

    @abstractmethod
    async def start(self) -> Any:
        """Start the bot. Must be called before using the bot."""

    @abstractmethod
    async def send(self, message: models.Message) -> Any:
        """Send a message with the bot."""

    # MARK: Subscriptions =====================================================

    def subscribe(self, bot: "ChatBot") -> None:
        """Subscribe a bot to the current bot by forwarding messages to it."""
        self.logger.debug("Creating subscription: %s -> %s", self, bot)
        self.subscribers.append(bot)

    def _handle_message(self, message: models.Message) -> None:
        """Handle a new message by sending it to all subscribers."""
        if not self.settings.is_active:
            return

        async def handler(bot: ChatBot, message: models.Message) -> None:
            try:
                await bot.send(message)
            except Exception as ex:
                raise models.DiscordException(
                    "Error sending message to subscriber."
                ) from ex

        for subscriber in self.subscribers:
            if not subscriber.settings.is_active:
                continue
            asyncio.create_task(handler(subscriber, message))

    # MARK: PAUSE/RESUME ======================================================

    def pause_bot(self) -> None:
        """Pause the bot."""
        self.logger.debug("Deactivating bot.")
        settings = self.database.load(self.settings)
        settings.is_active = False
        self.database.save(settings)

    def resume_bot(self) -> None:
        """Resume the bot."""
        self.logger.debug("Activating bot.")
        settings = self.database.load(self.settings)
        settings.is_active = True
        self.database.save(settings)
