from __future__ import annotations

import logging
from datetime import datetime
from itertools import cycle

import topgg
import aiohttp
import aiomysql

import discord
from discord.ext import commands, tasks
from discord.ext.ipc import Server

import config
from utils.conf import Config
from utils.db import guild_exists, add_guild


class FumeTool(commands.AutoShardedBot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo
    session: aiohttp.ClientSession
    pool: aiomysql.Pool
    topggpy: topgg.DBLClient
    ipc: Server
    launch_time: datetime
    log: logging.Logger
    user_blacklist: Config[bool]
    guild_blacklist: Config[bool]

    def __init__(self):
        description = "FumeTool - A fun and utility bot for your Discord server."

        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            description=description,
            heartbeat_timeout=180.0,
            intents=intents,
            help_command=None,
        )

        self.status_items: cycle = cycle([])

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        self.bot_app_info = await self.application_info()

        self.user_blacklist: Config[bool] = Config("data/user_blacklist.json")
        self.guild_blacklist: Config[bool] = Config("data/guild_blacklist.json")

        self.topggpy = topgg.DBLClient(bot=self, token=self.config.topgg_token)
        # noinspection PyTypeChecker
        self.ipc = Server(
            self,
            secret_key=self.config.ipc_secret_key,
            standard_port=self.config.ipc_standard_port,
            multicast_port=self.config.ipc_multicast_port,
        )

        for _extension in self.config.initial_extensions:
            try:
                await self.load_extension(_extension)
                self.log.info(f"Loaded extension {_extension}.")

            except Exception as e:
                self.log.error(f"Failed to load extension {_extension}.", exc_info=e)

    @tasks.loop(minutes=15)
    async def _update_status_items(self):
        self.status_items = cycle(
            [
                f"on {len(self.guilds)} servers | /help",
                "/invite | /vote | /community",
                "https://fumes.top/fumetool",
            ]
        )

    @tasks.loop(seconds=10)
    async def _change_status(self):
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(next(self.status_items)),
        )

    async def on_ready(self) -> None:
        self.launch_time = datetime.utcnow()

        self._update_status_items.start()
        self._change_status.start()

        self.log.info("FumeTool is ready.")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.author.id in self.user_blacklist:
            return

        if message.guild and message.guild.me in message.mentions:
            await message.reply(content="Hello there! Use `/help` to get started.")

    async def on_guild_join(self, guild) -> None:
        if guild.id in self.guild_blacklist:
            return await guild.leave()

        if not await guild_exists(self.pool, guild_id=guild.id):
            return await add_guild(self.pool, guild_id=guild.id)

    async def start(self, **kwargs) -> None:
        await super().start(config.token, reconnect=True)

    async def close(self) -> None:
        await super().close()
        await self.session.close()
        self.pool.close()
        await self.pool.wait_closed()

    @property
    def config(self):
        return __import__("config")

    @property
    def embed_color(self) -> int:
        return self.config.embed_color

    @property
    def uptime(self) -> str:
        delta_uptime = datetime.utcnow() - self.launch_time
        return (
            f"{delta_uptime.days}d, {delta_uptime.seconds // 3600}h, "
            f"{(delta_uptime.seconds // 60) % 60}m, "
            f"{delta_uptime.seconds % 60}s"
        )

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    @discord.utils.cached_property
    def webhook(self) -> discord.Webhook:
        return discord.Webhook.partial(
            id=self.config.webhook_id,
            token=self.config.webhook_token,
            session=self.session,
        )
