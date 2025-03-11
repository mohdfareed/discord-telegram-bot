__all__ = ["ChatBot"]

import asyncio
import logging
from abc import abstractmethod
from typing import Any

from . import broker, models


class ChatBot:
    """Chat bot that connects to a chat brokage service."""

    def __init__(self, broker: broker.ChatBroker) -> None:
        self.logger = logging.getLogger(type(self).__name__)
        self.handlers: list[models.MessageHandler] = []
        self.broker = broker

    @abstractmethod
    def start(self) -> Any: ...

    @abstractmethod
    def stop(self) -> Any: ...

    def register_message_handler(self, handler: models.MessageHandler) -> None:
        """Register a message handler."""
        self.handlers.append(handler)

    def handle_message(self, message: models.Message) -> None:
        """Handle a message by running all message handlers."""

        async def handle(
            handler: models.MessageHandler, message: models.Message
        ) -> None:
            try:
                await handler(message)
            except Exception as ex:
                raise models.DiscordException(
                    "Error running Discord message handler."
                ) from ex

        for handler in self.handlers:
            asyncio.create_task(handle(handler, message))
