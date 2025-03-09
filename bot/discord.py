__all__ = ["start_bot", "register_message_handler"]

import asyncio
import logging
from typing import Callable, Coroutine

import discord
from discord.ext import commands

from bot import models

MessageHandler = Callable[[models.Message], Coroutine[None, None, None]]

intents = discord.Intents.none()
intents.guild_messages = True
intents.message_content = True

logger = logging.getLogger(__name__)
message_handlers: list[MessageHandler] = []
bot = commands.Bot(command_prefix="!", intents=intents)


async def start_bot(token: str) -> None:
    """Start the bot."""
    await bot.start(token)


def register_message_handler(handler: MessageHandler) -> None:
    """Register a message handler."""
    message_handlers.append(handler)


@bot.event
async def on_ready() -> None:
    if not bot.user:
        raise RuntimeError("Bot failed to log in.")
    logger.info(f"Discord bot logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message) -> None:
    logger.debug(f"Received Discord message: {message.content}")
    msg = models.Message.from_discord(message)

    for handler in message_handlers:
        asyncio.create_task(handle_message(handler, msg))
    await bot.process_commands(message)


async def handle_message(
    handler: MessageHandler, message: models.Message
) -> None:
    try:
        await handler(message)
    except Exception as ex:
        raise models.DiscordException("Error running message handler.") from ex
