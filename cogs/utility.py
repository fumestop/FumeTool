import json
import asyncio
from contextlib import suppress

import discord
from discord import app_commands
from discord.ext import commands

import httpx
import aiohttp
import wikipediaapi
from steam.webapi import WebAPI
from steam.steamid import SteamID
from steam.enums import EPersonaState
import googletrans

# from easygoogletranslate import EasyGoogleTranslate

from utils.cd import cooldown_level_0, cooldown_level_1


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("config.json") as json_file:
            data = json.load(json_file)

        self.steam_api_key = data["steam_api_key"]
        self.weather_api_key = data["weather_api_key"]

        self.steamAPI = WebAPI(self.steam_api_key)

        self.poll_reaction_emojis = {
            1: "1\N{variation selector-16}\N{combining enclosing keycap}",
            2: "2\N{variation selector-16}\N{combining enclosing keycap}",
            3: "3\N{variation selector-16}\N{combining enclosing keycap}",
            4: "4\N{variation selector-16}\N{combining enclosing keycap}",
            5: "5\N{variation selector-16}\N{combining enclosing keycap}",
            6: "6\N{variation selector-16}\N{combining enclosing keycap}",
            7: "7\N{variation selector-16}\N{combining enclosing keycap}",
            8: "8\N{variation selector-16}\N{combining enclosing keycap}",
            9: "9\N{variation selector-16}\N{combining enclosing keycap}",
            10: "\N{keycap ten}",
        }

    @app_commands.command(name="avatar", description="Get the avatar of a user.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _avatar(self, ctx: discord.Interaction, member: discord.Member = None):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        member = member or ctx.user

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.set_image(url=member.avatar.url)

        return await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="userinfo", description="Get information about a user.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _user_info(self, ctx: discord.Interaction, member: discord.Member = None):
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
            name="Activity", value=member.activity.name if member.activity else "None"
        )

        roles = [role.mention for role in member.roles[1:]]
        embed.add_field(
            name="Server Roles",
            value="|".join(roles) if roles else "None",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(
        name="serverinfo", description="Get information about the server."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _server_info(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        bot_count = 0
        human_count = 0

        for i in ctx.guild.members:
            if i.bot:
                bot_count += 1
            else:
                human_count += 1

        embed = discord.Embed(colour=self.bot.embed_color)

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

    @app_commands.command(
        name="roleinfo", description="Get information about a server role."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _role_info(self, ctx: discord.Interaction, role: discord.Role):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        embed = discord.Embed(colour=self.bot.embed_color)

        count = len(
            [
                member
                for member in ctx.guild.members
                if discord.utils.get(member.roles, name=role.name)
            ]
        )

        perms = role.permissions
        perm_list = (
            "**Can kick members:** {}\n**Can ban members**: {}\n**Can change nickname:** {}"
            "\n**Can connect to voice channels:** {}"
            "\n**Can create instant invites:** {}\n**Can deafen members:** {}\n**Can embed links:** {}"
            "\n**Can use external emojis:** {}\n**Can manage channel:** {}\n**Can manage emojis:** {}"
            "\n**Can manage messages:** {}\n**Can manage nicknames:** {}"
            "\n**Can manage roles:** {}\n**Can manage server:** {}"
            "\n**Can mention everyone:** {}\n**Can move members:** {}\n**Can mute members:** {}"
            "\n**Can read message history:** {}\n**Can send messages:** {}\n**Can speak:** {}"
            "\n**Can use voice activity:** {}"
            "\n**Can manage webhooks:** {}\n**Can add reactions:** {}\n**Can view audit logs:** {}".format(
                perms.kick_members,
                perms.ban_members,
                perms.change_nickname,
                perms.connect,
                perms.create_instant_invite,
                perms.deafen_members,
                perms.embed_links,
                perms.external_emojis,
                perms.manage_channels,
                perms.manage_emojis,
                perms.manage_messages,
                perms.manage_nicknames,
                perms.manage_roles,
                perms.manage_guild,
                perms.mention_everyone,
                perms.move_members,
                perms.mute_members,
                perms.read_message_history,
                perms.send_messages,
                perms.speak,
                perms.use_voice_activation,
                perms.manage_webhooks,
                perms.add_reactions,
                perms.view_audit_log,
            )
        )

        perm_list = perm_list.replace("True", "Yes").replace('"', "")
        perm_list = perm_list.replace("False", "No").replace('"', "")

        created = f"<t:{int(role.created_at.timestamp())}:F> (<t:{int(role.created_at.timestamp())}:R>)"

        embed.description = (
            f"**Name:** {role.name} | {role.mention}\n**ID:** {role.id}\n**Color:** `{role.color}`"
            f"\n**Created:** {created}"
            f"\n**Position:** {role.position}**\nUser count:** {count}\n\n"
            f"**Mentionable:** "
            f"{str(role.mentionable).replace('True', 'Yes').replace('False', 'No')}"
            f"\n**Displayed separately:** "
            f"{str(role.hoist).replace('True', 'Yes').replace('False', 'No')}\n"
            + perm_list
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="roles", description="Get a list of all server roles.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _roles(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        if not ctx.guild.roles:
            return await ctx.edit_original_response(content="No roles found!")

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

    @app_commands.command(
        name="steam", description="Get information about a Steam user."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _steam(self, ctx: discord.Interaction, community_id: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        # noinspection PyUnresolvedReferences
        steam_id = SteamID.from_url(f"https://steamcommunity.com/id/{community_id}")

        steam_id = steam_id or community_id

        try:
            # noinspection PyUnresolvedReferences
            steam_user = self.steamAPI.ISteamUser.GetPlayerSummaries_v2(
                steamids=steam_id
            )["response"]["players"][0]

        except IndexError:
            return await ctx.edit_original_response(
                content="No such user found! "
                "Make sure you are using a valid Steam Community ID/URL."
            )

        # noinspection PyUnresolvedReferences
        bans = self.steamAPI.ISteamUser.GetPlayerBans_v1(steamids=steam_id)["players"][
            0
        ]

        vac_banned = bans["VACBanned"]
        community_banned = bans["CommunityBanned"]

        ban_info = {"VAC Banned": vac_banned, "Community Banned": community_banned}

        if vac_banned:
            ban_info["VAC Bans"] = bans["NumberOfVACBans"]
            ban_info["Days Since Last VAC Ban"] = bans["DaysSinceLastBan"]

        if steam_user["communityvisibilitystate"] != 3:
            embed = discord.Embed(colour=self.bot.embed_color)

            embed.description = "This profile is private."
            embed.title = steam_user["personaname"]
            embed.url = steam_user["profileurl"]
            embed.set_thumbnail(url=steam_user["avatarfull"])

            for _key, _value in ban_info.items():
                embed.add_field(name=_key, value=_value, inline=True)

            return await ctx.edit_original_response(embed=embed)

        # noinspection PyUnresolvedReferences
        group_count = len(
            self.steamAPI.ISteamUser.GetUserGroupList_v1(steamid=steam_id)["response"][
                "groups"
            ]
        )

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(
                    f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
                    f"?key={self.steam_api_key}&steamid={steam_id}"
                    f"&include_played_free_games=1%format=json"
                ) as res:
                    games = await res.json()
                    games = games["response"]

        except asyncio.TimeoutError:
            pass

        try:
            games_played = games["game_count"]

        except KeyError:
            games_played = 0

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

        fields = {
            "Status": state,
            "Created on": creation_date,
            "Group Count": group_count,
            "Games Owned": games_played,
        }

        if state == EPersonaState.Offline.name:
            if last_online is not None:
                fields["Last Online"] = last_online

        if game_name:
            fields["Currently Playing"] = game_name

        fields.update(ban_info)

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = steam_user["personaname"]
        embed.colour = self.bot.embed_color
        embed.url = steam_user["profileurl"]
        embed.set_thumbnail(url=steam_user["avatarfull"])

        for _key, _value in fields.items():
            embed.add_field(name=_key, value=_value, inline=True)

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(
        name="translate", description="Translate text from one language into another."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _translate(self, ctx: discord.Interaction, language: str, text: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        translator = googletrans.Translator(timeout=httpx.Timeout(10.0))

        try:
            translation = translator.translate(text, dest=language)

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

    @app_commands.command(name="define", description="Get the definition of a word.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _define(self, ctx: discord.Interaction, word: str):
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
            embed.add_field(name=f"Example", value=definition["example"], inline=False)

        if definition["synonyms"]:
            embed.add_field(name="Synonyms", value=", ".join(definition["synonyms"]))

        if definition["antonyms"]:
            embed.add_field(name="Antonyms", value=", ".join(definition["antonyms"]))

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(
        name="urban", description="Get the definition of a word from Urban Dictionary."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _urban(self, ctx: discord.Interaction, word: str):
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

    @app_commands.command(
        name="wikipedia", description="Get the summary of a Wikipedia article."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _wikipedia(self, ctx: discord.Interaction, query: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        wiki = wikipediaapi.Wikipedia("FumeTool (contact@fumes.top)", "en")
        page = wiki.page(query)

        if not page.exists():
            return await ctx.edit_original_response(content="No such page found!")

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = page.title
        embed.url = page.fullurl
        embed.description = page.summary + f"\n\n[**Read More**]({page.fullurl})"

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(
        name="covid", description="Get COVID-19 statistics for a country."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _covid(self, ctx: discord.Interaction, country: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        embed = discord.Embed(colour=self.bot.embed_color)

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(
                    f"https://disease.sh/v3/covid-19/countries/{country}"
                ) as res:
                    if res.status == 404:
                        return await ctx.edit_original_response(
                            content="No such country found!"
                        )

                    elif res.status == 200:
                        res = await res.json()

                        embed.title = "COVID-19"
                        embed.description = f"Statistics for {res['country']}"

                        embed.set_thumbnail(url=res["countryInfo"]["flag"])

                        embed.add_field(
                            name="Last Updated",
                            value=f"<t:{int(res['updated'] // 1000)}:R> (<t:{int(res['updated'] // 1000)}:F>)",
                        )
                        embed.add_field(
                            name="Total Cases (Confirmed)",
                            value=f"{res['cases']} (+{res['todayCases']})",
                        )
                        embed.add_field(name="Active", value=res["active"])
                        embed.add_field(
                            name="Recovered",
                            value=f"{res['recovered']} (+{res['todayRecovered']})",
                        )
                        embed.add_field(name="Critical", value=res["critical"])
                        embed.add_field(
                            name="Deaths",
                            value=f"{res['deaths']} (+{res['todayDeaths']})",
                        )

                        await ctx.edit_original_response(embed=embed)

                    else:
                        return await ctx.edit_original_response(
                            content="An API-side error occurred while processing your "
                            "request. Please try again later."
                        )

        except asyncio.TimeoutError:
            return await ctx.edit_original_response(
                content="The API timed out. Please try again later."
            )

    @app_commands.command(
        name="weather", description="Get the weather report for a city."
    )
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
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(
                    f"https://api.weatherapi.com/v1/current.json?key={self.weather_api_key}&q={city}"
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

                        embed.set_thumbnail(url=f"https:{current['condition']['icon']}")

                        embed.add_field(
                            name="Temperature",
                            value=f"{current['temp_c']}°C"
                            if temperature_scale.value == "c"
                            else f"{current['temp_f']}°F",
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
                            value=f"{current['feelslike_c']}°C"
                            if temperature_scale.value == "c"
                            else f"{current['feelslike_f']}°F",
                        )
                        embed.add_field(
                            name="Humidity", value=f"{current['humidity']}%"
                        )
                        embed.add_field(
                            name="Wind Speed",
                            value=f"{current['wind_kph']} km/h"
                            if speed_scale.value == "k"
                            else f"{current['wind_mph']} mph",
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
                            value=f"{current['vis_km']} km"
                            if speed_scale.value == "k"
                            else f"{current['vis_miles']} miles",
                        )

                        await ctx.edit_original_response(embed=embed)

        except asyncio.TimeoutError:
            return await ctx.edit_original_response(
                content="The API timed out. Please try again later."
            )

    @app_commands.command(name="poll", description="Create a poll.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _poll(self, ctx: discord.Interaction, title: str, choices: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

        choices = choices.split(",")
        choices = [choice.strip() for choice in choices]

        if 2 > len(choices) > 10:
            return await ctx.edit_original_response(
                content="The number of choices have to be between 2 and 10."
            )

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = title
        embed.description = ""

        for _index, _choice in enumerate(choices, 1):
            embed.description += f"{self.poll_reaction_emojis[_index]}. {_choice}\n"

        await ctx.edit_original_response(embed=embed)

        sent_response = await ctx.original_response()
        for _reaction in list(self.poll_reaction_emojis.values())[: len(choices)]:
            await sent_response.add_reaction(_reaction)


async def setup(bot):
    await bot.add_cog(Utility(bot))
