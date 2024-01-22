import aiohttp

import discord
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_0
from utils.tools import owo_fy


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="owo", description="Uwu-fyies your text.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _owo(self, ctx: discord.Interaction, text: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        await ctx.edit_original_response(content=owo_fy(text))

    @app_commands.command(name="meme", description="Send a random meme.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _meme(self, ctx: discord.Interaction):
        embed = discord.Embed(colour=self.bot.embed_colour)

        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme/10") as res:
                if res.status != 200:
                    return await ctx.edit_original_response(content="An API-side error occurred. "
                                                                    "Please try again in sometime.")

                res = await res.json()
                res = res["memes"]

                for meme in res:
                    if meme["nsfw"]:
                        continue

                    else:
                        break

        embed.title = f"[**{meme['subreddit']}** by **{meme['author']}**]({[meme['postLink']]})"
        embed.description = meme["title"]
        embed.set_image(url=meme["url"])

        embed.set_footer(text=f"{meme['ups']} \U0001f44d {meme['downs']} \U0001f44e {meme['comments']} \U0001f5e8")

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="dog", description="Send a random dog\"s image.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _dog(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as res:
                if res.status != 200:
                    return await ctx.edit_original_response(content="An API-side error occurred. "
                                                                    "Please try again in sometime.")

                res = await res.json()
                img_url = res["message"]

        embed = discord.Embed(colour=self.bot.embed_colour)
        embed.title = "Random Doggo \U0001f436"
        embed.set_image(url=img_url)

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="cat", description="Send a random cat\"s image.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _cat(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession() as session:
            async with session.get("https://shibe.online/api/cats") as res:
                if res.status != 200:
                    return await ctx.edit_original_response(content="An API-side error occurred. "
                                                                    "Please try again in sometime.")

                res = await res.json()
                img_url = res[0]

        embed = discord.Embed(colour=self.bot.embed_colour)
        embed.title = "Random Kitty \U0001f431"
        embed.set_image(url=img_url)

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="bird", description="Send a random bird\"s image.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _bird(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession() as session:
            async with session.get("https://shibe.online/api/birds") as res:
                if res.status != 200:
                    return await ctx.edit_original_response(content="An API-side error occurred. "
                                                                    "Please try again in sometime.")

                res = await res.json()
                img_url = res[0]

        embed = discord.Embed(colour=self.bot.embed_colour)
        embed.title = "Random Birdie \U0001F60D"
        embed.set_image(url=img_url)

        await ctx.edit_original_response(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
