__all__ = ["TelegramBot"]

import telegram
from telegram.ext import Application, CommandHandler, ContextTypes

from bot import core


class TelegramBot(core.ChatBot):
    def __init__(self, token: str, broker: core.ChatBroker) -> None:
        super().__init__(broker)
        self.token = token

        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("get_id", self.get_id_command))
        application.add_handler(CommandHandler("subs", self.subs_command))
        application.add_handler(CommandHandler("sub", self.subscribe_command))
        application.add_handler(
            CommandHandler("unsub", self.unsubscribe_command)
        )
        self.app = application

    async def start(self) -> None:
        self.logger.info("Starting Telegram bot.")
        if not self.app.updater:
            self.logger.error("Telegram bot not initialized properly.")
            return

        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

    async def stop(self) -> None:
        self.logger.debug("Stopping Telegram bot.")
        if self.app.updater:
            await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    async def send_message(self, message: core.Message) -> None:
        if self.app.bot is None:
            self.logger.error("Telegram bot not initialized.")
            return

        for chat_id in self.broker.get_subscribers(str(message.chat_id)):
            self.logger.debug(
                f"Sending message from {message.chat_id} to {chat_id}"
            )
            await self.app.bot.send_message(chat_id, message.text)

    async def get_id_command(
        self, update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.logger.debug(f"Received get_id command: {update.message}")
        if not await self._is_from_admin(update):
            return
        if update.message is None or update.message.from_user is None:
            return

        self.logger.info(f"Sending chat ID to {update.message.from_user}")
        await update.message.from_user.send_message(
            f"{update.message.chat_id}"
        )

    async def subs_command(
        self, update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.logger.debug(f"Received subs command: {update.message}")
        if update.message is None or update.message.from_user is None:
            return
        if not await self._is_from_admin(update):
            return

        self.logger.info(
            f"Getting subscriptions count for {update.message.chat_id}"
        )
        subs = self.broker.get_subscriptions(str(update.message.chat_id))
        await update.message.from_user.send_message(f"Subscriptions: {subs}")

    async def subscribe_command(
        self, update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.logger.debug(f"Received subscribe command: {update.message}")
        if update.message is None or update.message.from_user is None:
            return
        if not await self._is_from_admin(update):
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

        self.logger.info(f"Subscribing {chat_id} to {publisher_id}")
        self.broker.subscribe(str(chat_id), publisher_id)
        await update.message.reply_text("Subscribed!")

    async def unsubscribe_command(
        self, update: telegram.Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.logger.debug(f"Received unsubscribe command: {update.message}")
        if update.message is None or update.message.from_user is None:
            return
        if not await self._is_from_admin(update):
            return

        self.logger.info(
            f"Unsubscribing {update.message.chat_id} from publishers."
        )
        self.broker.unsubscribe_all(str(update.message.chat_id))
        await update.message.reply_text("Unsubscribed!")

    async def _is_from_admin(self, update: telegram.Update) -> bool:
        if update.message is None or update.message.from_user is None:
            return False
        member = await update.get_bot().get_chat_member(
            update.message.chat_id, update.message.from_user.id
        )

        return (
            update.message.chat.type == update.message.chat.PRIVATE
            or member.status
            in [
                telegram.constants.ChatMemberStatus.ADMINISTRATOR,
                telegram.constants.ChatMemberStatus.OWNER,
            ]
        )
