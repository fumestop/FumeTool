import math
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Returns the API and bot latency.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _ping(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.description = "**Pong!**"

        ms = self.bot.latency * 1000

        embed.add_field(name="API latency (Heartbeat)", value=f"`{int(ms)} ms`")

        t1 = datetime.utcnow().strftime("%f")

        await ctx.edit_original_response(embed=embed)

        t2 = datetime.utcnow().strftime("%f")
        diff = int(math.fabs((int(t2) - int(t1)) / 1000))

        embed.add_field(name="Bot latency (Round-trip)", value=f"`{diff} ms`")

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="web", description="Shows web resources about FumeTool.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _web(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Website", url="https://fumes.top"))
        view.add_item(
            discord.ui.Button(label="Homepage", url="https://fumes.top/fumetool")
        )
        view.add_item(
            discord.ui.Button(label="GitHub", url="https://github.com/FumeStop")
        )
        view.add_item(
            discord.ui.Button(
                label="Linkedin", url="https://www.linkedin.com/company/fumestop"
            )
        )
        view.add_item(
            discord.ui.Button(label="Twitter (X)", url="https://x.com/fumestop")
        )

        await ctx.edit_original_response(
            content="Here are the links to various FumeTool resources on the web:",
            view=view,
        )

    @app_commands.command(
        name="invite", description="Shows the invite link for FumeTool."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _invite(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Invite",
                url="https://fumes.top/fumetool/invite",
            )
        )

        await ctx.edit_original_response(
            content="Thank you for choosing me!", view=view
        )

    @app_commands.command(name="vote", description="Vote for FumeTool on Top.GG!")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _vote(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(label="Vote", url="https://fumes.top/fumetool/vote")
        )

        await ctx.edit_original_response(
            content="Thank you for choosing to vote for me!", view=view
        )

    @app_commands.command(
        name="review", description="Leave a review for FumeTool on Top.GG!"
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _review(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(label="Review", url="https://fumes.top/fumetool/review")
        )

        await ctx.edit_original_response(
            content="Thank you for reviewing me!", view=view
        )

    @app_commands.command(
        name="community",
        description="Sends the invite to the official community server.",
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _community(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Community Server Invite", url="https://fumes.top/community"
            )
        )

        await ctx.edit_original_response(
            content="Join the community server for help & updates!", view=view
        )


async def setup(bot):
    await bot.add_cog(General(bot))
