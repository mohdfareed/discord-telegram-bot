__all__ = ["bot", "start_bot", "register_message_handler"]

import asyncio
import logging

import discord
from discord.ext import commands

from bot import models

intents = discord.Intents.none()
intents.guild_messages = True
intents.message_content = True

logger = logging.getLogger(__name__)
message_handlers: list[models.MessageHandler] = []
subscriptions: models.Subscriptions = models.Subscriptions.load()
bot = commands.Bot(command_prefix="/", intents=intents)


def start_bot(token: str) -> None:
    """Start the bot (blocking)."""
    logger.info("Starting Discord bot.")
    bot.run(token)


def register_message_handler(handler: models.MessageHandler) -> None:
    """Register a message handler."""
    message_handlers.append(handler)


@bot.event
async def on_ready() -> None:
    if not bot.user:
        raise RuntimeError("Bot failed to log in.")
    logger.info(f"Discord bot logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return
    msg = models.Message.from_discord(message)
    logger.debug(f"Received Discord message: {msg}")

    for handler in message_handlers:
        asyncio.create_task(handle_message(handler, msg))
    await bot.process_commands(message)


async def handle_message(
    handler: models.MessageHandler, message: models.Message
) -> None:
    try:
        await handler(message)
    except Exception as ex:
        raise models.DiscordException("Error running message handler.") from ex


@bot.command()
@commands.has_permissions(administrator=True)
async def get_id(ctx: commands.Context[commands.Bot]) -> None:
    msg = models.Message.from_discord(ctx.message)
    logger.debug(f"Received get_id command: {msg}")
    author = ctx.message.author

    id = subscriptions.get_publisher(msg.chat_id)
    logger.info(f"Sending chat ID to {author}: {id}")
    await author.send(f"{id}")
