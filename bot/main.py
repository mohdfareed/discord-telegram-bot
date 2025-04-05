import asyncio
import logging
from typing import Annotated

import typer

from bot import core, discord, telegram
from bot.core import models

from . import APP_NAME

logger = logging.getLogger(__name__)
app = typer.Typer(
    name=APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def main(
    debug_mode: Annotated[
        bool,
        typer.Option(
            "--debug", "-d", help="Log debug messages to the console."
        ),
    ] = False,
) -> None:
    """Main entry point for the bot package."""
    app_settings = models.Settings()
    core.logging.setup_logging(debug_mode, app_settings.data_path / "bot.log")


@app.command()
def start() -> None:
    """Start the bots."""
    asyncio.run(start_bots())


async def start_bots() -> None:
    # dependencies
    app_settings = models.Settings()
    db = core.JSONDataBase(app_settings.data_path)
    broker = core.ChatBroker(db)

    # bots setup
    discord_bot = discord.DiscordBot(
        app_settings.discord_bot_token, broker, db
    )
    telegram_bot = telegram.TelegramBot(
        app_settings.telegram_bot_token, broker, db
    )
    discord_bot.subscribe(telegram_bot)

    try:  # start app
        await telegram_bot.start()
        await discord_bot.start()
    finally:  # cleanup
        print()
        await telegram_bot.stop()
