import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help", description="A list of all the commands provided by FumeTool."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _help(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        embed = discord.Embed(colour=self.bot.embed_colour)

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


async def setup(bot):
    await bot.add_cog(Help(bot))
