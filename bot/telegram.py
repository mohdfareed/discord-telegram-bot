__all__ = ["TelegramBot"]

from typing import override

import telegram
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import filters as telegram_filters

from bot import core

INVALID_MARKDOWN = (
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
)


class TelegramBot(core.ChatBot):
    def __init__(
        self, token: str, broker: core.ChatBroker, db: core.Database
    ) -> None:
        super().__init__(broker, db)
        self.token = token

        channel_command_filter = telegram_filters.COMMAND & (
            telegram_filters.ChatType.GROUP
            | telegram_filters.ChatType.SUPERGROUP
            | telegram_filters.ChatType.CHANNEL
        )

        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("sub", self.subscribe_command))
        application.add_handler(CommandHandler("reset", self.reset_command))
        application.add_handler(
            CommandHandler(
                "id", self.get_id_command, filters=channel_command_filter
            )
        )
        self.app = application

    @override
    async def start(self) -> None:
        self.logger.info("Starting Telegram bot.")
        if not self.app.updater:
            self.logger.error("Telegram bot not initialized properly.")
            return

        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=True)

    async def stop(self) -> None:
        """Stop the bot. Must be called before exiting the program."""
        self.logger.debug("Stopping Telegram bot.")
        if self.app.updater:
            await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    @override
    async def send(self, message: core.Message) -> None:
        message.text = message.text.replace("@everyone", "").strip()
        for chat_id in self.broker.get_subscribers(str(message.chat_id)):
            if not message.attachments:
                await self.app.bot.send_message(chat_id, message.text)
                continue
            for attachment in message.attachments:
                await self.app.bot.send_photo(
                    chat_id,
                    attachment,
                    caption=message.text,
                    parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
                )

    # MARK: Commands ==========================================================

    async def get_id_command(
        self, update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.logger.debug(f"Received id command: {update}")
        message = update.message or update.channel_post
        if message is None:
            return

        (sender, chat) = message.from_user, message.sender_chat
        if sender is None:
            if chat is None:
                return

            try:
                username = (message.text or "").split(" ")[1]
            except (ValueError, IndexError):
                await message.reply_text(
                    "Invalid admin username\\. Expected the username of the "
                    "admin who will receive the chat ID: `/id <username>`",
                    parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
                )
                return
            sender = next(
                (
                    admin
                    for admin in await chat.get_administrators()
                    if admin.user.username == username
                ),
                None,
            )
            if sender is None:
                await message.reply_text(
                    "No admin found with the provided username."
                )
                return
        else:
            sender = await self.app.bot.get_chat_member(
                message.chat_id, sender.id
            )
        if sender.status not in (
            telegram.constants.ChatMemberStatus.ADMINISTRATOR,
            telegram.constants.ChatMemberStatus.OWNER,
        ):
            return

        self.logger.info(f"Sending chat ID to: {sender}")
        await sender.user.send_message(
            f"`{message.chat_id}`",
            parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        )
        await message.delete()

    async def subscribe_command(
        self, update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:  # used in private chats
        self.logger.debug(f"Received subscribe command: {update}")
        if update.message is None or update.message.from_user is None:
            return
        if update.message.chat.type != telegram.constants.ChatType.PRIVATE:
            return

        try:
            publisher_id = (update.message.text or "").split(" ")[1]
            publisher_id = int(publisher_id)
            chat_id = (update.message.text or "").split(" ")[2]
            chat_id = int(chat_id)
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Invalid chat IDs\\. Expected two integers, the publisher "
                "chat ID and the listener chat ID: `/sub <pub_id> <chat_id>`",
                parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
            )
            return

        self.logger.info(f"Subscribing {chat_id} to {publisher_id}")
        self.broker.subscribe(str(chat_id), publisher_id)
        await update.message.reply_text("Subscribed.")
        if update.message:
            await update.message.delete()

    async def reset_command(
        self, update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:  # used in private chats
        self.logger.debug(f"Received unsubscribe command: {update}")
        if update.message is None or update.message.from_user is None:
            return
        if update.message.chat.type != telegram.constants.ChatType.PRIVATE:
            return

        self.logger.info(
            f"Unsubscribing {update.message.chat_id} from publishers."
        )
        self.broker.unsubscribe_all(str(update.message.chat_id))
        await update.message.reply_text("Unsubscribed.")
        if update.message:
            await update.message.delete()

    @staticmethod
    async def _parse(msg: telegram.Message) -> core.Message:
        """Create a message from a Telegram message."""
        attachments = [
            bytes(await (await photo.get_file()).download_as_bytearray())
            for photo in msg.photo
        ]

        return core.Message(
            text=msg.text or "", chat_id=msg.chat_id, attachments=attachments
        )
