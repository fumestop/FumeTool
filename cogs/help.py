from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0

if TYPE_CHECKING:
    from bot import FumeTool


class Help(commands.Cog):
    def __init__(self, bot: FumeTool):
        self.bot: FumeTool = bot

    @app_commands.command(name="help")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _help(self, ctx: discord.Interaction):
        """Shows a list of all the commands provided by FumeTool."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Command List"
        embed.description = 'Here"s a list of available commands: '

        embed.add_field(
            name="General",
            value=f"`ping`, `uptime`, `web`, `invite`, `vote`, `review`, `community`",
            inline=False,
        )

        embed.add_field(
            name="Fun",
            value=f"`owo`, `meme`, `dog`, `cat`, `bird`",
            inline=False,
        )

        embed.add_field(
            name="Development",
            value=f"`dns`, `whois`, `ip`, `scan`, `dstatus`, `gstatus`, `pypi`, `npm`, "
            f"`screenshot`, `tts`",
            inline=False,
        )

        embed.add_field(
            name="Utility",
            value=f"`avatar`, `userinfo`, `serverinfo`, `roles`, `roleinfo`, `define`, `urban`, "
            f"`wikipedia`, `steam`, `translate`, `weather`, `poll`",
            inline=False,
        )

        embed.add_field(
            name="Tags",
            value=f"`tag view`, `tag raw`, `tag create`, `tag alias`, `tag all`, `tag list`, `tag info`, "
            f"`tag search`, `tag edit`, `tag delete`, `tag purge`, `tag claim`",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)


async def setup(bot: FumeTool):
    await bot.add_cog(Help(bot))
