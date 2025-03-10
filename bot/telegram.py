__all__ = ["send_message"]

import logging

import telegram
from telegram.ext import Application, CommandHandler, ContextTypes

from bot import models

logger = logging.getLogger(__name__)
subscriptions: models.Subscriptions = models.Subscriptions.load()
bot: telegram.Bot | None = None


def start_bot(token: str) -> None:
    """Start the bot (blocking)."""
    global bot

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get_id", get_id_command))
    application.add_handler(CommandHandler("subs", subs_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    bot = application.bot
    logger.info("Starting Telegram bot.")
    application.run_polling()


async def send_message(message: models.Message) -> None:
    """Send a message via Telegram."""
    global bot
    if bot is None:
        logger.error("Telegram bot not initialized.")
        return

    for chat_id in subscriptions.get_subscribers(message.chat_id):
        logger.debug(f"Sending message from {message.chat_id} to {chat_id}")
        await bot.send_message(chat_id, message.text)


async def help_command(
    update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return
    await update.message.reply_text(
        "The bot broadcasts messages from Discord to Telegram.\n"
        "Use the /get_id command to get the chat ID of the current chat.\n"
        "This ID can be used to subscribe this channel to Discord messages.\n"
        "Use the /subscribe <telegram_chat_id> <discord_chat_id> command to subscribe."
    )


async def get_id_command(
    update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
) -> None:
    logger.debug(f"Received get_id command: {update.message}")
    if update.message is None:
        return
    if update.message.from_user is None:
        return

    member = await update.get_bot().get_chat_member(
        update.message.chat_id, update.message.from_user.id
    )

    if (
        update.message.chat.type != update.message.chat.PRIVATE
        and member.status
        not in [
            telegram.constants.ChatMemberStatus.ADMINISTRATOR,
            telegram.constants.ChatMemberStatus.OWNER,
        ]
    ):
        return

    logger.info(f"Sending chat ID to {update.message.from_user}")
    await update.message.from_user.send_message(f"{update.message.chat_id}")


async def subs_command(
    update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
) -> None:
    logger.debug(f"Received subs command: {update.message}")
    if update.message is None:
        return
    if update.message.from_user is None:
        return

    member = await update.get_bot().get_chat_member(
        update.message.chat_id, update.message.from_user.id
    )

    if (
        update.message.chat.type != update.message.chat.PRIVATE
        and member.status
        not in [
            telegram.constants.ChatMemberStatus.ADMINISTRATOR,
            telegram.constants.ChatMemberStatus.OWNER,
        ]
    ):
        return

    logger.info(f"Getting subscriptions count for {update.message.chat_id}")
    count = subscriptions.get_subs_count(update.message.chat_id)
    await update.message.reply_text(f"Subscriptions: {count}")


async def subscribe_command(
    update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
) -> None:
    logger.debug(f"Received subscribe command: {update.message}")
    if update.message is None:
        return
    if update.message.from_user is None:
        return

    member = await update.get_bot().get_chat_member(
        update.message.chat_id, update.message.from_user.id
    )

    if (
        update.message.chat.type != update.message.chat.PRIVATE
        and member.status
        not in [
            telegram.constants.ChatMemberStatus.ADMINISTRATOR,
            telegram.constants.ChatMemberStatus.OWNER,
        ]
    ):
        return

    chat_id = (update.message.text or "").split(" ")[1]
    publisher_id = (update.message.text or "").split(" ")[2]

    try:
        chat_id = int(chat_id)
        publisher_id = int(publisher_id)
    except ValueError:
        await update.message.reply_text(
            "Invalid chat IDs. Expected two integers (chat ID and Discord ID)."
        )
        return

    logger.info(f"Subscribing {chat_id} to {publisher_id}")
    subscriptions.subscribe(chat_id, publisher_id)
    await update.message.reply_text("Subscribed!")


async def unsubscribe_command(
    update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
) -> None:
    logger.debug(f"Received unsubscribe command: {update.message}")
    if update.message is None:
        return
    if update.message.from_user is None:
        return

    member = await update.get_bot().get_chat_member(
        update.message.chat_id, update.message.from_user.id
    )

    if (
        update.message.chat.type != update.message.chat.PRIVATE
        and member.status
        not in [
            telegram.constants.ChatMemberStatus.ADMINISTRATOR,
            telegram.constants.ChatMemberStatus.OWNER,
        ]
    ):
        return

    logger.info(f"Unsubscribing {update.message.chat_id} from publishers.")
    subscriptions.unsubscribe_all(update.message.chat_id)
    await update.message.reply_text("Unsubscribed!")
