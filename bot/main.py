import asyncio
from typing import Annotated

import dotenv
import typer

from bot import discord, logging, models, telegram

from . import APP_NAME

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
    dotenv.load_dotenv()
    app_settings = models.Settings()
    logging.setup_logging(debug_mode, app_settings.data_path / "bot.log")


@app.command()
def start() -> None:
    """Start the bot."""
    app_settings = models.Settings()
    discord.register_message_handler(telegram.send_message)
    asyncio.run(discord.start_bot(app_settings.discord_bot_token))
