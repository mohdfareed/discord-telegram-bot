__all__ = ["DiscordBot"]

import discord
from discord.ext import commands

from bot import core


class DiscordBot(core.ChatBot, commands.Cog):
    def __init__(
        self, token: str, broker: core.ChatBroker, db: core.Database
    ) -> None:
        super().__init__(broker, db)
        self.token = token

        intents = discord.Intents.none()
        intents.guilds = True
        intents.guild_messages = True
        intents.message_content = True

        @commands.command()
        @commands.has_permissions(administrator=True)
        async def pause(ctx: commands.Context[commands.Bot]) -> None:
            self.pause_bot()
            await ctx.message.delete()

        @commands.command()
        @commands.has_permissions(administrator=True)
        async def resume(ctx: commands.Context[commands.Bot]) -> None:
            self.resume_bot()
            await ctx.message.delete()

        @commands.command()
        @commands.has_permissions(administrator=True)
        async def id(ctx: commands.Context[commands.Bot]) -> None:
            await self.get_id(ctx)
            await ctx.message.delete()

        @commands.command()
        @commands.has_permissions(administrator=True)
        async def reset(ctx: commands.Context[commands.Bot]) -> None:
            await self.reset(ctx)
            await ctx.message.delete()

        self.bot = commands.Bot(command_prefix="/", intents=intents)
        self.bot.add_command(pause)
        self.bot.add_command(resume)
        self.bot.add_command(id)
        self.bot.add_command(reset)

        self.bot.add_listener(self.on_ready)
        self.bot.add_listener(self.on_message)

    async def start(self) -> None:
        self.logger.info("Starting Discord bot.")
        await self.bot.start(self.token)

    async def on_ready(self) -> None:
        if not self.bot.user:
            raise RuntimeError("Bot failed to log in.")
        self.logger.info(f"Discord bot logged in as {self.bot.user}")

    @commands.has_permissions(administrator=True)
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return

        msg = self._parse(message)
        self._handle_message(msg)
        await self.bot.process_commands(message)

    # MARK: Commands ==========================================================

    async def send(self, message: core.Message) -> None:
        await super().send(message)
        self.logger.error(
            "Sending messages with Discord bot is not supported: %s", message
        )
        # raise NotImplementedError(
        #     "Discord bot does not support sending messages.", message
        # )

    async def get_id(self, ctx: commands.Context[commands.Bot]) -> None:
        msg = self._parse(ctx.message)
        self.logger.debug(f"Received get_id command: {msg}")
        author = ctx.message.author

        id = self.broker.get_publisher_id(str(msg.chat_id))
        self.logger.info(f"Sending chat ID to {author}: {id}")
        await author.send(f"{id}")

    async def reset(self, ctx: commands.Context[commands.Bot]) -> None:
        msg = self._parse(ctx.message)
        self.logger.debug(f"Received reset_subs command: {msg}")
        author = ctx.message.author

        self.broker.reset_publisher_id(str(msg.chat_id))
        self.logger.info(f"Resetting subscriptions for {msg.chat_id}")
        await author.send("Subscriptions reset.")

    @staticmethod
    def _parse(msg: discord.Message) -> core.Message:
        """Create a message from a Discord message."""
        return core.Message(text=msg.content, chat_id=msg.channel.id)
