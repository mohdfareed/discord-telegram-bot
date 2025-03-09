__all__ = ["send_message"]


import logging

from bot import models

logger = logging.getLogger(__name__)


async def send_message(message: models.Message) -> None:
    """Send a message via Telegram."""
    logger.info(f"Sending message via Telegram: {message.text}")
