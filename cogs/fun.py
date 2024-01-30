from __future__ import annotations
from typing import TYPE_CHECKING

import random

import aiohttp

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0
from utils.tools import owo_fy

if TYPE_CHECKING:
    from bot import FumeTool


class Fun(commands.Cog):
    def __init__(self, bot: FumeTool):
        self.bot: FumeTool = bot

    @app_commands.command(name="owo")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _owo(self, ctx: discord.Interaction, text: str):
        """Uwu-fyies your text.

        Parameters
        ----------
        text: str
            The text to be uwu-fied.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        await ctx.edit_original_response(content=owo_fy(text))

    @app_commands.command(name="meme")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _meme(self, ctx: discord.Interaction):
        """Send a random meme from Reddit."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        embed = discord.Embed(colour=self.bot.embed_color)

        _subreddits = [
            "memes",
            "dankmemes",
            "me_irl",
            "wholesomememes",
            "comedyheaven",
        ]

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                f"https://meme-api.com/gimme/{random.choice(_subreddits)}/5"
            ) as res:
                if res.status != 200:
                    return await ctx.edit_original_response(
                        content="An API-side error occurred. "
                        "Please try again in sometime."
                    )

                res = await res.json()
                res = res["memes"]

                for meme in res:
                    if meme["nsfw"]:
                        continue

                    else:
                        break

        embed.title = f"**/r/{meme['subreddit']} by {meme['author']}**"
        embed.url = meme["postLink"]
        embed.description = meme["title"]
        embed.set_image(url=meme["url"])

        embed.set_footer(text=f"{meme['ups']} \U0001f44d")

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="dog")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _dog(self, ctx: discord.Interaction):
        """Send a random dog's image."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get("https://shibe.online/api/shibes") as res:
                if res.status != 200:
                    return await ctx.edit_original_response(
                        content="An API-side error occurred. "
                        "Please try again in sometime."
                    )

                res = await res.json()
                img_url = res[0]

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Random Doggo \U0001f436 \U0001F60D"
        embed.set_image(url=img_url)

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="cat")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _cat(self, ctx: discord.Interaction):
        """Send a random cat's image."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get("https://shibe.online/api/cats") as res:
                if res.status != 200:
                    return await ctx.edit_original_response(
                        content="An API-side error occurred. "
                        "Please try again in sometime."
                    )

                res = await res.json()
                img_url = res[0]

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Random Kitty \U0001f431 \U0001F60D"
        embed.set_image(url=img_url)

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="bird")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _bird(self, ctx: discord.Interaction):
        """Send a random bird's image."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get("https://shibe.online/api/birds") as res:
                if res.status != 200:
                    return await ctx.edit_original_response(
                        content="An API-side error occurred. "
                        "Please try again in sometime."
                    )

                res = await res.json()
                img_url = res[0]

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Random Birdie \U0001f426 \U0001F60D"
        embed.set_image(url=img_url)

        await ctx.edit_original_response(embed=embed)


async def setup(bot: FumeTool):
    await bot.add_cog(Fun(bot))
