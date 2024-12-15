from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import asyncio
from contextlib import suppress

import httpx
import aiohttp
import discord
import googletrans
import wikipediaapi
from discord import app_commands
from discord.ext import commands
from steam.enums import EPersonaState
from steam.webapi import WebAPI
from steam.steamid import SteamID
from discord.ext.menus.views import ViewMenuPages

from utils.cd import cooldown_level_0, cooldown_level_1
from utils.tools import format_boolean_text
from utils.paginators import RolePaginatorSource

if TYPE_CHECKING:
    from bot import FumeTool


class Utility(commands.Cog):
    def __init__(self, bot: FumeTool):
        self.bot: FumeTool = bot

        self.steam = WebAPI(self.bot.config.STEAM_API_KEY)

        self.poll_reaction_emojis = {
            1: "1\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            2: "2\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            3: "3\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            4: "4\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            5: "5\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            6: "6\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            7: "7\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            8: "8\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            9: "9\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            10: "\N{KEYCAP TEN}",
        }

    @app_commands.command(name="avatar")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _avatar(
        self, ctx: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Get the avatar of a user.

        Parameters
        ----------
        member : Optional[discord.Member]
            The member whose avatar is to be fetched. Defaults to the user.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        member = member or ctx.user

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.set_image(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )

        return await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="userinfo")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _user_info(
        self, ctx: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Get information about a user.

        Parameters
        ----------
        member : Optional[discord.Member]
            The member whose information is to be fetched. Defaults to the user.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        member = member or ctx.user

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.set_thumbnail(url=member.guild_avatar or member.avatar)

        embed.add_field(name="Username", value=member.name)
        embed.add_field(name="Global Name", value=member.global_name)
        embed.add_field(name="Server Nickname", value=member.nick or "None")
        embed.add_field(name="ID", value=f"`{member.id}`")
        embed.add_field(name="Bot", value="Yes" if member.bot else "No")

        embed.add_field(
            name="Registered",
            value=f"<t:{int(member.created_at.timestamp())}:F> (<t:{int(member.created_at.timestamp())}:R>)",
        )
        embed.add_field(
            name="Joined Server",
            value=f"<t:{int(member.joined_at.timestamp())}:F> (<t:{int(member.joined_at.timestamp())}:R>)",
        )

        join_list = list()

        for guild_user in ctx.guild.members:
            join_list.append(guild_user.joined_at)

        join_list.sort()

        embed.add_field(
            name="Join Position", value=join_list.index(member.joined_at) + 1
        )

        embed.add_field(name="Status", value=str(member.status).capitalize())
        embed.add_field(
            name="Activity",
            value=member.activity.name if member.activity else "None",
        )

        roles = [role.mention for role in member.roles[1:]]
        embed.add_field(
            name="Server Roles",
            value="|".join(roles) if roles else "None",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="serverinfo")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _server_info(self, ctx: discord.Interaction):
        """Get information about the server."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        bot_count = 0
        human_count = 0

        for _member in ctx.guild.members:
            if _member.bot:
                bot_count += 1
            else:
                human_count += 1

        embed = discord.Embed(colour=self.bot.embed_color)

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.add_field(name="Name", value=ctx.guild.name)
        embed.add_field(name="ID", value=f"`{ctx.guild.id}`")

        embed.add_field(
            name="Server Owner",
            value=f"`{ctx.guild.owner}` | {ctx.guild.owner.mention}",
        )
        embed.add_field(name="Owner ID", value=ctx.guild.owner_id)

        embed.add_field(
            name="Created",
            value=f"<t:{int(ctx.guild.created_at.timestamp())}:F> (<t:{int(ctx.guild.created_at.timestamp())}:R>)",
        )

        embed.add_field(name="Total Members", value=ctx.guild.member_count)
        embed.add_field(name="Humans", value=human_count)
        embed.add_field(name="Bots", value=bot_count)

        embed.add_field(name="Boosts", value=ctx.guild.premium_subscription_count)
        embed.add_field(name="Boost Level", value=ctx.guild.premium_tier)

        if ctx.guild.vanity_url:
            embed.add_field(name="Vanity URL", value=ctx.guild.vanity_url)

        roles = [role.mention for role in ctx.guild.roles[1:]]
        embed.add_field(
            name="Server Roles",
            value=" | ".join(reversed(roles)) if roles else "None",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="roles")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _roles(self, ctx: discord.Interaction):
        """Get a list of all server roles."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        if not ctx.guild.roles:
            return await ctx.edit_original_response(
                content="This server does not have any roles yet."
            )

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "List of Server Roles"
        embed.set_thumbnail(url=ctx.guild.icon.url)

        roles = ctx.guild.roles
        roles = [role.mention for role in roles[1:]]

        embed.description = " | ".join(reversed(roles))

        embed.set_footer(
            text=f"Total Roles: {len(roles)} | Ordered from highest to lowest"
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="roleinfo")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _role_info(self, ctx: discord.Interaction, role: discord.Role):
        """Get information about a server role.

        Parameters
        ----------
        role : discord.Role
            The role whose information is to be fetched.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        permissions = role.permissions

        general_server_permissions = (
            f"```\n"
            f"View Channels: {permissions.view_channel}\n"
            f"Manage Channels: {permissions.manage_channels}\n"
            f"Manage Roles: {permissions.manage_roles}\n"
            f"Create Expressions: {permissions.create_expressions}\n"
            f"Manage Expressions: {permissions.manage_expressions}\n"
            f"View Audit Log: {permissions.view_audit_log}\n"
            f"View Server Insights: {permissions.view_guild_insights}\n"
            f"Manage Webhooks: {permissions.manage_webhooks}\n"
            f"Manage Server: {permissions.manage_guild}\n"
            f"```"
        )

        membership_permissions = (
            f"```\n"
            f"Create Invite: {permissions.create_instant_invite}\n"
            f"Change Nickname: {permissions.change_nickname}\n"
            f"Manage Nicknames: {permissions.manage_nicknames}\n"
            f"Kick Members: {permissions.kick_members}\n"
            f"Ban Members: {permissions.ban_members}\n"
            f"Timeout Members: {permissions.moderate_members}\n"
            f"```"
        )

        text_channel_permissions = (
            f"```\n"
            f"Send Messages: {permissions.send_messages}\n"
            f"Send Messages in Threads: {permissions.send_messages_in_threads}\n"
            f"Create Public Threads: {permissions.create_public_threads}\n"
            f"Create Private Threads: {permissions.create_private_threads}\n"
            f"Embed Links: {permissions.embed_links}\n"
            f"Attach Files: {permissions.attach_files}\n"
            f"Add Reactions: {permissions.add_reactions}\n"
            f"Use External Emoji: {permissions.use_external_emojis}\n"
            f"Use External Stickers: {permissions.use_external_stickers}\n"
            f"Mention @everyone, @here, and All Roles: {permissions.mention_everyone}\n"
            f"Manage Messages: {permissions.manage_messages}\n"
            f"Manage Threads: {permissions.manage_threads}\n"
            f"Read Message History: {permissions.read_message_history}\n"
            f"Send Text-to-Speech Messages: {permissions.send_tts_messages}\n"
            f"Use Application Commands: {permissions.use_application_commands}\n"
            f"Send Voice Messages: {permissions.send_voice_messages}\n"
            f"```"
        )

        voice_channel_permissions = (
            f"```\n"
            f"Connect: {permissions.connect}\n"
            f"Speak: {permissions.speak}\n"
            f"Video: {permissions.stream}\n"
            f"Use Activities: {permissions.use_embedded_activities}\n"
            f"Use Soundboard: {permissions.use_soundboard}\n"
            f"Use External Sounds: {permissions.use_external_sounds}\n"
            f"Use Voice Activity: {permissions.use_voice_activation}\n"
            f"Priority Speaker: {permissions.priority_speaker}\n"
            f"Mute Members: {permissions.mute_members}\n"
            f"Deafen Members: {permissions.deafen_members}\n"
            f"Move Members: {permissions.move_members}\n"
            # f"Set Voice Channel Status: {permissions.set_voice_channel_status}\n")
            f"```"
        )

        stage_channel_permissions = (
            f"```\n" f"Request to Speak: {permissions.request_to_speak}\n" f"```"
        )

        events_permissions = (
            f"```\n"
            # f"Create Events: {permissions.create_events}\n"
            f"Manage Events: {permissions.manage_events}\n"
            f"```"
        )
        advanced_permissions = (
            f"```\n" f"Administrator: {permissions.administrator}\n" f"```"
        )

        permissions_list = [
            {
                "name": "General Server Permissions",
                "value": format_boolean_text(general_server_permissions),
            },
            {
                "name": "Membership Permissions",
                "value": format_boolean_text(membership_permissions),
            },
            {
                "name": "Text Channel Permissions",
                "value": format_boolean_text(text_channel_permissions),
            },
            {
                "name": "Voice Channel Permissions",
                "value": format_boolean_text(voice_channel_permissions),
            },
            {
                "name": "Stage Channel Permissions",
                "value": format_boolean_text(stage_channel_permissions),
            },
            {
                "name": "Events Permissions",
                "value": format_boolean_text(events_permissions),
            },
            {
                "name": "Advanced Permissions",
                "value": format_boolean_text(advanced_permissions),
            },
        ]

        pages = RolePaginatorSource(
            entries=permissions_list,
            role=role,
            position=sorted([role for role in ctx.guild.roles], reverse=True).index(
                role
            )
            + 1,
        )
        paginator = ViewMenuPages(
            source=pages,
            timeout=None,
            delete_message_after=False,
            clear_reactions_after=True,
        )

        await ctx.edit_original_response(content="\U0001f44c")
        await paginator.start(ctx)

    @app_commands.command(name="define")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _define(self, ctx: discord.Interaction, word: str):
        """Get the definition of a word.

        Parameters
        ----------
        word : str
            The word to get the definition of.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(
                    f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                ) as res:
                    res = await res.json()

        except asyncio.TimeoutError:
            return await ctx.edit_original_response(
                content="The API timed out. Please try again later."
            )

        if (
            isinstance(res, dict)
            and "title" in res.keys()
            and res["title"] == "No Definitions Found"
        ):
            return await ctx.edit_original_response(content="No such word found!")

        data = res[0]
        meaning = data["meanings"][0]
        definition = meaning["definitions"][0]

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = data["word"].title()
        embed.description = definition["definition"]

        with suppress(KeyError):
            embed.add_field(
                name="Pronunciation",
                value=f"[{data['phonetics'][0]['text']}]({data['phonetics'][0]['audio']})",
            )

        with suppress(KeyError):
            embed.add_field(name="Origin", value=data["origin"])

        with suppress(KeyError):
            embed.add_field(
                name="Part of Speech", value=meaning["partOfSpeech"].capitalize()
            )

        with suppress(KeyError):
            embed.add_field(
                name=f"Example", value=definition["example"], inline=False
            )

        if definition["synonyms"]:
            embed.add_field(name="Synonyms", value=", ".join(definition["synonyms"]))

        if definition["antonyms"]:
            embed.add_field(name="Antonyms", value=", ".join(definition["antonyms"]))

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="urban")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _urban(self, ctx: discord.Interaction, word: str):
        """Get the definition of a word from Urban Dictionary.

        Parameters
        ----------
        word : str
            The word to get the definition of.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(
                    f"https://api.urbandictionary.com/v0/define?term={word.replace(' ', '%20')}"
                ) as res:
                    res = await res.json()

        except asyncio.TimeoutError:
            return await ctx.edit_original_response(
                content="The API timed out. Please try again later."
            )

        if not res["list"]:
            return await ctx.edit_original_response(content="No such word found!")

        res = res["list"][0]

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = word.title()
        embed.url = res["permalink"]
        embed.description = (
            res["definition"]
            .split("\n")[0]
            .replace("[", "")
            .replace("]", "")
            .replace("1. ", "")
        )

        if res["example"]:
            embed.add_field(
                name="Example",
                value=res["example"].replace("[", "").replace("]", ""),
            )

        embed.set_footer(
            text=f"{res['thumbs_up']} \U0001f44d {res['thumbs_down']} \U0001f44e"
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="wikipedia")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _wikipedia(self, ctx: discord.Interaction, query: str):
        """Get the summary of a Wikipedia article.

        Parameters
        ----------
        query : str
            The article to get the summary of.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        wiki = wikipediaapi.Wikipedia("FumeTool (contact@fumes.top)", "en")
        page = wiki.page(query)

        if not page.exists():
            return await ctx.edit_original_response(content="No such page found!")

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = page.title
        embed.url = page.fullurl
        embed.description = page.summary + f"\n\n[Read More]({page.fullurl})"

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="steam")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _steam(self, ctx: discord.Interaction, community_id: str):
        """Get information about a Steam user.

        Parameters
        ----------
        community_id : str
            The Steam Community ID or URL of the user.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        # noinspection PyUnresolvedReferences
        steam_id = SteamID.from_url(f"https://steamcommunity.com/id/{community_id}")
        steam_id = steam_id or community_id

        try:
            # noinspection PyUnresolvedReferences
            steam_user = self.steam.ISteamUser.GetPlayerSummaries_v2(
                steamids=steam_id
            )["response"]["players"][0]

        except IndexError:
            return await ctx.edit_original_response(
                content="No such user found! "
                "Make sure you are using a valid Steam Community ID/URL."
            )

        # noinspection PyUnresolvedReferences
        bans = self.steam.ISteamUser.GetPlayerBans_v1(steamids=steam_id)["players"][
            0
        ]

        if steam_user["communityvisibilitystate"] != 3:
            embed = discord.Embed(colour=self.bot.embed_color)

            embed.description = "This profile is private."
            embed.title = steam_user["personaname"]
            embed.url = steam_user["profileurl"]
            embed.set_thumbnail(url=steam_user["avatarfull"])

            embed.add_field(
                name="VAC Banned", value=format_boolean_text(bans["VACBanned"])
            )
            embed.add_field(
                name="Community Banned",
                value=format_boolean_text(bans["CommunityBanned"]),
            )

            if bans["VACBanned"]:
                embed.add_field(name="VAC Bans", value=bans["NumberOfVACBans"])
                embed.add_field(
                    name="Days Since Last VAC Ban", value=bans["DaysSinceLastBan"]
                )

            return await ctx.edit_original_response(embed=embed)

        # noinspection PyUnresolvedReferences
        group_count = len(
            self.steam.ISteamUser.GetUserGroupList_v1(steamid=steam_id)["response"][
                "groups"
            ]
        )

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(
                    f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
                    f"?key={self.bot.config.STEAM_API_KEY}&steamid={steam_id}"
                    f"&include_played_free_games=1%format=json"
                ) as res:
                    games = await res.json()
                    games = games["response"]

        except asyncio.TimeoutError:
            pass

        try:
            games_owned = games["game_count"]

        except KeyError:
            games_owned = 0

        state = EPersonaState(steam_user["personastate"]).name
        game_name = None

        if "gameid" in steam_user.keys():
            state = "In-game"
            game_id = steam_user["gameid"]

            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as session:
                    async with session.get(
                        f"https://store.steampowered.com/api/appdetails?appids={game_id}"
                    ) as res:
                        game_name = await res.json()
                        game_name = game_name[game_id]["data"]["name"]

            except asyncio.TimeoutError:
                pass

        last_online = None

        try:
            last_online = f"<t:{steam_user['lastlogoff']}:R>"

        except KeyError:
            pass

        creation_date = (
            f"<t:{steam_user['timecreated']}:F> (<t:{steam_user['timecreated']}:R>)"
        )

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = steam_user["personaname"]
        embed.colour = self.bot.embed_color
        embed.url = steam_user["profileurl"]
        embed.set_thumbnail(url=steam_user["avatarfull"])

        embed.add_field(
            name="VAC Banned", value=format_boolean_text(bans["VACBanned"])
        )
        embed.add_field(
            name="Community Banned",
            value=format_boolean_text(bans["CommunityBanned"]),
        )

        if bans["VACBanned"]:
            embed.add_field(name="VAC Bans", value=bans["NumberOfVACBans"])
            embed.add_field(
                name="Days Since Last VAC Ban", value=bans["DaysSinceLastBan"]
            )

        embed.add_field(name="Status", value=state)
        embed.add_field(name="Created on", value=creation_date)
        embed.add_field(name="Group Count", value=group_count)
        embed.add_field(name="Games Owned", value=games_owned)

        if state == EPersonaState.Offline.name:
            if last_online is not None:
                embed.add_field(name="Last Online", value=last_online)

        if game_name:
            embed.add_field(name="Currently Playing", value=game_name)

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="translate")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _translate(self, ctx: discord.Interaction, language: str, text: str):
        """Translate text from one language into another.

        Parameters
        ----------
        language : str
            The language to translate the text into. Must be a valid ISO 639-1 language code.
        text : str
            The text to translate.
        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        async with googletrans.Translator(timeout=httpx.Timeout(10.0)) as translator:
            try:
                translation = await translator.translate(text, dest=language)

            except ValueError:
                return await ctx.edit_original_response(
                    content="Either an invalid or unsupported language was specified."
                )

            embed = discord.Embed(color=self.bot.embed_color)
            embed.title = "Translation"
            embed.description = translation.text

            embed.add_field(
                name="Detected Language",
                value=googletrans.LANGUAGES[translation.src].capitalize(),
            )
            embed.add_field(
                name="Target Language",
                value=googletrans.LANGUAGES[translation.dest].capitalize(),
            )
            if translation.extra_data["confidence"]:
                embed.add_field(
                    name="Confidence",
                    value=f"{translation.extra_data['confidence'] * 100}%",
                )
            embed.add_field(name="Pronunciation", value=translation.pronunciation)

            await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="weather")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    @app_commands.choices(
        temperature_scale=[
            app_commands.Choice(name="Celsius", value="c"),
            app_commands.Choice(name="Fahrenheit", value="f"),
        ]
    )
    @app_commands.choices(
        speed_scale=[
            app_commands.Choice(name="Kilometers", value="k"),
            app_commands.Choice(name="Miles", value="m"),
        ]
    )
    async def _weather(
        self,
        ctx: discord.Interaction,
        city: str,
        temperature_scale: app_commands.Choice[str] = None,
        speed_scale: app_commands.Choice[str] = None,
    ):
        """Get the weather report for a city.

        Parameters
        ----------
        city : str
            The city to get the weather report for.
        temperature_scale : Optional[app_commands.Choice[str]]
            The temperature scale to use. Defaults to Celsius.
        speed_scale : Optional[app_commands.Choice[str]]
            The speed scale to use. Defaults to Kilometers.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(
                    f"https://api.weatherapi.com/v1/current.json?key={self.bot.config.WEATHER_API_KEY}&q={city}"
                ) as res:
                    res = await res.json()

                    if "error" in res.keys() and res["error"]["code"] == 1006:
                        return await ctx.edit_original_response(
                            content="No such city found!"
                        )

                    elif "current" not in res.keys():
                        return await ctx.edit_original_response(
                            content="An API-side error occurred while processing your "
                            "request. Please try again later."
                        )
                    else:
                        temperature_scale = temperature_scale or app_commands.Choice(
                            name="Celsius", value="c"
                        )
                        speed_scale = speed_scale or app_commands.Choice(
                            name="Kilometers", value="k"
                        )

                        current = res["current"]
                        location = res["location"]

                        embed = discord.Embed(colour=self.bot.embed_color)

                        embed.title = (
                            f"Weather Report for {location['name']}, "
                            f"{location['region']}, {location['country']}"
                        )

                        embed.set_thumbnail(
                            url=f"https:{current['condition']['icon']}"
                        )

                        embed.add_field(
                            name="Temperature",
                            value=(
                                f"{current['temp_c']}°C"
                                if temperature_scale.value == "c"
                                else f"{current['temp_f']}°F"
                            ),
                        )
                        embed.add_field(
                            name="Local Time",
                            value=f"<t:{location['localtime_epoch']}:t>",
                        )
                        embed.add_field(
                            name="Last Updated",
                            value=f"<t:{current['last_updated_epoch']}:R>",
                        )
                        embed.add_field(
                            name="Condition", value=current["condition"]["text"]
                        )
                        embed.add_field(
                            name="Feels Like",
                            value=(
                                f"{current['feelslike_c']}°C"
                                if temperature_scale.value == "c"
                                else f"{current['feelslike_f']}°F"
                            ),
                        )
                        embed.add_field(
                            name="Humidity", value=f"{current['humidity']}%"
                        )
                        embed.add_field(
                            name="Wind Speed",
                            value=(
                                f"{current['wind_kph']} kmph"
                                if speed_scale.value == "k"
                                else f"{current['wind_mph']} mph"
                            ),
                        )
                        embed.add_field(
                            name="Wind Direction", value=current["wind_dir"]
                        )
                        embed.add_field(
                            name="Precipitation", value=f"{current['precip_mm']} mm"
                        )
                        embed.add_field(
                            name="Pressure", value=f"{current['pressure_mb']} mb"
                        )
                        embed.add_field(
                            name="Cloud Cover", value=f"{current['cloud']}%"
                        )
                        embed.add_field(
                            name="Visibility",
                            value=(
                                f"{current['vis_km']} km"
                                if speed_scale.value == "k"
                                else f"{current['vis_miles']} miles"
                            ),
                        )

                        await ctx.edit_original_response(embed=embed)

        except asyncio.TimeoutError:
            return await ctx.edit_original_response(
                content="The API timed out. Please try again later."
            )

    @app_commands.command(name="poll", description="Create a poll.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _poll(
        self,
        ctx: discord.Interaction,
        title: str,
        choices: str,
        channel: Optional[discord.TextChannel] = None,
    ):
        """Create a poll.

        Parameters
        ----------
        title : str
            The title of the poll.
        choices : str
            The choices for the poll. Separate each choice with a comma.
        channel : Optional[discord.TextChannel]
            The channel to send the poll in. Defaults to the current channel.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        channel = channel or ctx.channel

        choices = choices.split(",")
        choices = [choice.strip() for choice in choices]

        if 2 >= len(choices) >= 10:
            return await ctx.edit_original_response(
                content="The number of choices have to be between 2 and 10."
            )

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = title
        embed.description = ""

        for _index, _choice in enumerate(choices, 1):
            embed.description += f"{self.poll_reaction_emojis[_index]}. {_choice}\n"

        sent_message = await channel.send(embed=embed)

        await ctx.edit_original_response(content="Poll created successfully!")

        for _reaction in list(self.poll_reaction_emojis.values())[: len(choices)]:
            await sent_message.add_reaction(_reaction)


async def setup(bot: FumeTool):
    await bot.add_cog(Utility(bot))
