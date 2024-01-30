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
        """A list of all the commands provided by FumeTool."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Command List"
        embed.description = 'Here"s a list of available commands: '

        embed.add_field(
            name="General",
            value=f"`ping`, `web`, `invite`, `vote`, `review`, `community`",
            inline=False,
        )

        embed.add_field(
            name="Fun",
            value=f"`owo`, `meme`, `dog`, `cat`, `bird`",
            inline=False,
        )

        embed.add_field(
            name="Development",
            value=f"`dns`, `ip`, `scan`, `screenshot`, `whois`, `dstatus`, `gstatus`, `pypi`, `npm`, "
            f"`tts`",
            inline=False,
        )

        embed.add_field(
            name="Utility",
            value=f"`user`, `server`, `bot`, `role`, `roles`, `steam`, `translate`, `define`, `urban`, "
            f"`wikipedia`, `weather`, `poll`, `avatar`",
            inline=False,
        )

        embed.add_field(
            name="Tags",
            value=f"`tag`, `traw`, `tadd`, `tlist`, `tedit`, `tdel`, `tclaim`, `talias`, `tinfo`, `tsearch`",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)


async def setup(bot: FumeTool):
    await bot.add_cog(Help(bot))
