from __future__ import annotations
from typing import Any

import logging
from datetime import datetime
from itertools import cycle

import topgg
import aiohttp
import aiomysql

import discord
from discord.app_commands import CommandTree
from discord.ext import commands, tasks
from discord.ext.ipc import Server

import config
from utils.db import (
    guild_exists,
    add_guild,
    is_blacklisted_user,
    is_blacklisted_guild,
)


class FumeTree(CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await is_blacklisted_user(self.client.pool, interaction.user.id):
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(
                "You are blacklisted from using this bot. To appeal, join the community server."
            )
            return False

        if interaction.guild and await is_blacklisted_guild(
            self.client.pool, interaction.guild.id
        ):
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(
                "This server is blacklisted from using this bot. To appeal, join the community server."
            )
            await interaction.guild.leave()
            return False

        return True


class FumeTool(commands.AutoShardedBot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo
    session: aiohttp.ClientSession
    pool: aiomysql.Pool
    topggpy: topgg.DBLClient
    ipc: Server
    log: logging.Logger

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
            tree_cls=FumeTree,
        )

        self._launch_time: datetime = Any
        self._status_items: cycle = Any

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        self.bot_app_info = await self.application_info()

        self.topggpy = topgg.DBLClient(bot=self, token=self.config.TOPGG_TOKEN)
        # noinspection PyTypeChecker
        self.ipc = Server(
            self,
            secret_key=self.config.IPC_SECRET_KEY,
            standard_port=self.config.IPC_STANDARD_PORT,
            multicast_port=self.config.IPC_MULTICAST_PORT,
        )

        for _extension in self.config.INITIAL_EXTENSIONS:
            try:
                await self.load_extension(_extension)
                self.log.info(f"Loaded extension {_extension}.")

            except Exception as e:
                self.log.error(f"Failed to load extension {_extension}.", exc_info=e)

    @tasks.loop(minutes=15)
    async def _update_status_items(self):
        self._status_items = cycle(
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
            activity=discord.Game(next(self._status_items)),
        )

    async def on_ready(self) -> None:
        self._launch_time = datetime.now()

        self._update_status_items.start()
        self._change_status.start()

        self.log.info("FumeTool is ready.")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if await is_blacklisted_user(self.pool, message.author.id):
            return

        if message.guild and await is_blacklisted_guild(self.pool, message.guild.id):
            return await message.guild.leave()

        if message.guild and message.guild.me in message.mentions:
            await message.reply(content="Hello there! Use `/help` to get started.")

    async def on_guild_join(self, guild) -> None:
        if await is_blacklisted_guild(self.pool, guild.id):
            return await guild.leave()

        if not await guild_exists(self.pool, guild_id=guild.id):
            return await add_guild(self.pool, guild_id=guild.id)

    async def start(self, **kwargs) -> None:
        await super().start(config.TOKEN, reconnect=True)

    async def close(self) -> None:
        await super().close()
        await self.session.close()

        self.pool.close()
        await self.pool.wait_closed()

        self._update_status_items.stop()
        self._change_status.stop()

    @property
    def config(self):
        return __import__("config")

    @property
    def embed_color(self) -> int:
        return self.config.EMBED_COLOR

    @property
    def launch_time(self) -> datetime:
        return self._launch_time

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    @discord.utils.cached_property
    def webhook(self) -> discord.Webhook:
        return discord.Webhook.partial(
            id=self.config.WEBHOOK_ID,
            token=self.config.WEBHOOK_TOKEN,
            session=self.session,
        )
