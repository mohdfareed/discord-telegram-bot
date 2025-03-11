__all__ = ["DiscordBot"]

import discord
from discord.ext import commands

from bot import core


class DiscordBot(core.ChatBot, commands.Cog):
    def __init__(self, token: str, broker: core.ChatBroker) -> None:
        super().__init__(broker)
        self.token = token

        intents = discord.Intents.none()
        intents.guilds = True
        intents.guild_messages = True
        intents.message_content = True

        @commands.command()
        async def get_id(ctx: commands.Context[commands.Bot]) -> None:
            await self.get_id(ctx)

        @commands.command()
        async def reset_subs(ctx: commands.Context[commands.Bot]) -> None:
            await self.reset_subs(ctx)

        self.bot = commands.Bot(command_prefix="/", intents=intents)
        self.bot.add_command(get_id)
        self.bot.add_command(reset_subs)
        self.bot.add_listener(self.on_ready)
        self.bot.add_listener(self.on_message)

    async def start(self) -> None:
        self.logger.info("Starting Discord bot.")
        await self.bot.start(self.token)

    async def stop(self) -> None:
        self.logger.info("Stopping Discord bot.")
        await self.bot.close()

    async def on_ready(self) -> None:
        if not self.bot.user:
            raise RuntimeError("Bot failed to log in.")
        self.logger.info(f"Discord bot logged in as {self.bot.user}")

    async def on_message(self, message: discord.Message) -> None:
        msg = core.Message.from_discord(message)
        self.logger.debug(f"Received Discord message: {msg}")
        if message.author == self.bot.user:
            return
        self.handle_message(msg)
        await self.bot.process_commands(message)

    @commands.has_permissions(administrator=True)
    async def get_id(self, ctx: commands.Context[commands.Bot]) -> None:
        msg = core.Message.from_discord(ctx.message)
        self.logger.debug(f"Received get_id command: {msg}")
        author = ctx.message.author

        id = self.broker.get_publisher_id(str(msg.chat_id))
        self.logger.info(f"Sending chat ID to {author}: {id}")
        await author.send(f"{id}")

    @commands.has_permissions(administrator=True)
    async def reset_subs(self, ctx: commands.Context[commands.Bot]) -> None:
        msg = core.Message.from_discord(ctx.message)
        self.logger.debug(f"Received reset_subs command: {msg}")
        author = ctx.message.author

        self.broker.reset_publisher_id(str(msg.chat_id))
        self.logger.info(f"Resetting subscriptions for {msg.chat_id}")
        await author.send("Subscriptions reset.")
