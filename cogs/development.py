from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import random
import socket
import string
import asyncio
from io import BytesIO
from contextlib import suppress

import gtts
import whois
import aiohttp
import discord
import validators
from dns import resolver
from PIL import Image, UnidentifiedImageError
from discord import app_commands
from discord.ext import commands

from utils.cd import cooldown_level_1

if TYPE_CHECKING:
    from bot import FumeTool


class Development(commands.Cog):
    def __init__(self, bot: FumeTool):
        self.bot: FumeTool = bot

        self.overall_status = {
            "All Systems Operational": "\U0001f7e2",
            "Partial System Outage": "\U0001f7e2",
            "Major Service Outage": "\U0001f534",
        }

        self.component_status = {
            "Operational": "\U0001f7e2",
            "Degraded Performance": "\U0001f7e1",
            "Partial Outage": "\U0001f7e2",
            "Major Outage": "\U0001f534",
        }

    @app_commands.command(name="dns")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    @app_commands.choices(
        record=[
            app_commands.Choice(name="All records", value="*"),
            app_commands.Choice(name="A", value="A"),
            app_commands.Choice(name="AAAA", value="AAAA"),
            app_commands.Choice(name="CNAME", value="CNAME"),
            app_commands.Choice(name="MX", value="MX"),
            app_commands.Choice(name="NS", value="NS"),
            app_commands.Choice(name="PTR", value="PTR"),
            app_commands.Choice(name="SOA", value="SOA"),
            app_commands.Choice(name="SRV", value="SRV"),
            app_commands.Choice(name="TXT", value="TXT"),
        ]
    )
    async def _dns(
        self,
        ctx: discord.Interaction,
        domain: str,
        record: Optional[app_commands.Choice[str]] = None,
    ):
        """Looks up the various DNS records of a domain.

        Parameters
        ----------
        domain : str
            The domain to look up.
        record : Optional[app_commands.Choice[str]]
            The type  of record to look up.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        record = record or app_commands.Choice(name="All records", value="*")

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "DNS Lookup"

        field = "```css\n"

        embed.add_field(name="Domain", value=f"`{domain}`")
        embed.add_field(name="Record Type", value=f"`{record.name}`")

        try:
            if record.value != "*":
                try:
                    answers = resolver.resolve(domain, record.value)

                    for _data in answers:
                        field += f"{_data.to_text()}\n"

                except resolver.NoAnswer:
                    field += f"No {record.value} record found.\n"

                except resolver.NoNameservers:
                    field += f"No {record.value} record found.\n"

                except resolver.Timeout:
                    return await ctx.edit_original_response(
                        content="The DNS operation timed out."
                    )

                finally:
                    embed.add_field(
                        name="Records", value=f"{field}```", inline=False
                    )

            else:
                for _record in [
                    "A",
                    "AAAA",
                    "CNAME",
                    "MX",
                    "NS",
                    "PTR",
                    "SOA",
                    "SRV",
                    "TXT",
                ]:
                    try:
                        answers = resolver.resolve(domain, _record)
                        for r_data in answers:
                            field += f"{_record} : {r_data.to_text()}\n"

                    except resolver.NoAnswer:
                        field += f"No `{_record}` record found\n"

                    except resolver.NoNameservers:
                        field += f"No `{_record}` record found.\n"

                    except resolver.Timeout:
                        await ctx.edit_original_response(
                            content="The DNS operation timed out."
                        )

                embed.add_field(name="Records", value=f"{field}```", inline=False)

        except resolver.NXDOMAIN:
            return await ctx.edit_original_response(
                content=f"Couldn't resolve host : `{domain}`"
            )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="whois")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _whois(self, ctx: discord.Interaction, domain: str):
        """Retrieves a domain's information from the WHOIS database.

        Parameters
        ----------
        domain : str
            The domain to look up.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not validators.domain(domain):
            return await ctx.edit_original_response(
                content=f"`{domain}` is not a valid domain."
            )

        try:
            dm_info = whois.whois(domain)

        except whois.parser.PywhoisError:
            return await ctx.edit_original_response(
                content=f"`{domain}` is not registered."
            )

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "WHOIS Lookup"

        domains = (
            "\n".join(dm_info["domain_name"])
            if isinstance(dm_info["domain_name"], list)
            else dm_info["domain_name"]
        )
        embed.add_field(name="Domain(s)", value=f"```css\n{domains}```")

        embed.add_field(name="Registrar", value=dm_info["registrar"])

        with suppress(KeyError):
            embed.add_field(name="WHOIS Server", value=dm_info["whois_server"])

        with suppress(AttributeError):
            creation_date = (
                dm_info["creation_date"][0]
                if isinstance(dm_info["creation_date"], list)
                else dm_info["creation_date"]
            )
            embed.add_field(
                name="Creation Date",
                value=f"<t:{int(creation_date.timestamp())}:F> (<t:{int(creation_date.timestamp())}:R>)",
            )

        with suppress(AttributeError):
            expiration_date = (
                dm_info["expiration_date"][0]
                if isinstance(dm_info["expiration_date"], list)
                else dm_info["expiration_date"]
            )
            embed.add_field(
                name="Expiration Date",
                value=f"<t:{int(expiration_date.timestamp())}:F> (<t:{int(expiration_date.timestamp())}:R>)",
            )

        with suppress(AttributeError):
            updated_date = (
                dm_info["updated_date"][0]
                if isinstance(dm_info["updated_date"], list)
                else dm_info["updated_date"]
            )
            embed.add_field(
                name="Updated Date",
                value=f"<t:{int(updated_date.timestamp())}:F> (<t:{int(updated_date.timestamp())}:R>)",
            )

        with suppress(KeyError):
            emails = (
                "\n".join(dm_info["emails"])
                if isinstance(dm_info["emails"], list)
                else "None"
            )
            embed.add_field(name="Emails", value=f"```css\n{emails}```")

        with suppress(KeyError):
            embed.add_field(name="DNSSEC", value=dm_info["dnssec"])
        with suppress(KeyError):
            embed.add_field(name="Organization", value=dm_info["org"])
        with suppress(KeyError):
            embed.add_field(name="Address", value=dm_info["address"])
        with suppress(KeyError):
            embed.add_field(name="City", value=dm_info["city"])
        with suppress(KeyError):
            embed.add_field(name="State", value=dm_info["state"])
        with suppress(KeyError):
            embed.add_field(name="Country", value=dm_info["country"])
        with suppress(KeyError):
            embed.add_field(
                name="Postal Code", value=dm_info["registrant_postal_code"]
            )

        with suppress(KeyError):
            nameservers = (
                "\n".join(dm_info["name_servers"])
                if isinstance(dm_info["name_servers"], list)
                else dm_info["name_servers"]
            )
            embed.add_field(name="Nameservers", value=f"```css\n{nameservers}```")

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="ip")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _ip(self, ctx: discord.Interaction, address: str):
        """Retrieves various information about an IP address.

        Parameters
        ----------
        address : str
            The IP address to look up.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not validators.ip_address.ipv4(address, cidr=False):
            if not validators.ip_address.ipv6(address, cidr=False):
                return await ctx.edit_original_response(
                    content=f"`{address}` is not a valid IP address."
                )

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(f"https://ipinfo.io/{address}/json") as res:
                if res.status == 200:
                    res = await res.json()

                    if "bogon" in res:
                        return await ctx.edit_original_response(
                            content="This IP is reserved for special use."
                        )

                    else:
                        embed = discord.Embed(colour=self.bot.embed_color)
                        embed.title = f"IP Lookup - {res['ip']}"
                        embed.url = f"https://ipinfo.io/{res['ip']}"

                        with suppress(KeyError):
                            embed.add_field(
                                name="Hostname", value="`" + res["hostname"] + "`"
                            )

                        with suppress(KeyError):
                            embed.add_field(name="Organization", value=res["org"])

                        with suppress(KeyError):
                            embed.add_field(
                                name="Anycast",
                                value="Yes" if res["anycast"] else "No",
                            )

                        with suppress(KeyError):
                            embed.add_field(name="Co-ordinates", value=res["loc"])

                        with suppress(KeyError):
                            embed.add_field(
                                name="Location",
                                value=f"{res['city']}, {res['region']}, {res['country']}",
                            )

                        with suppress(KeyError):
                            embed.add_field(name="Postal", value=res["postal"])

                        with suppress(KeyError):
                            embed.add_field(
                                name="Timezone",
                                value=res["timezone"].replace("_", " "),
                            )

                        await ctx.edit_original_response(embed=embed)

                elif res.status in [404, 400]:
                    return await ctx.edit_original_response(
                        content="Please enter a valid IP."
                    )

                else:
                    return await ctx.edit_original_response(
                        content="A API-side error occurred while processing "
                        "your request. Please try again later."
                    )

    @app_commands.command(name="scan")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _scan(self, ctx: discord.Interaction, host: str, port: int):
        """Scans a particular port on a host.

        Parameters
        ----------
        host : str
            The host to scan.
        port : int
            The port to scan.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if host in ["localhost", "0.0.0.0", "127.0.0.1"]:
            return await ctx.edit_original_response(
                content="\U000026a0 That host is forbidden."
            )

        if not validators.hostname(
            host,
            skip_ipv4_addr=False,
            skip_ipv6_addr=False,
            may_have_port=False,
            maybe_simple=False,
        ):
            return await ctx.edit_original_response(
                content=f"`{host}` is not a valid host."
            )

        if port not in range(0, 65536):
            return await ctx.edit_original_response(
                content=f"`{port}` is not a valid port. Valid ports are from `0` to `65535`."
            )

        try:
            host = socket.gethostbyname(host)

        except socket.gaierror:
            return await ctx.edit_original_response(
                content=f"Couldn't resolve host : `{host}`"
            )

        try:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.settimeout(10)

            res = _socket.connect_ex((host, port))

            if res == 0:
                await ctx.edit_original_response(
                    content=f"Port `{port}` on `{host}` is **OPEN**."
                )

            else:
                await ctx.edit_original_response(
                    content=f"Port `{port}` on `{host}` is **CLOSED**."
                )

        except socket.gaierror:
            return await ctx.edit_original_response(
                content=f"`{host}` is not a valid address."
            )

    @app_commands.command(name="dstatus")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _d_status(self, ctx: discord.Interaction):
        """Fetch Discord overall and component status."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                "https://srhpyqt94yxb.statuspage.io/api/v2/summary.json"
            ) as response:
                response = await response.json()

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = "Discord Status"

        comment = response["status"]["description"]
        api = response["components"][0]["status"].replace("_", " ").title()
        media_proxy = response["components"][5]["status"].replace("_", " ").title()
        push_notifications = (
            response["components"][8]["status"].replace("_", " ").title()
        )
        voice = response["components"][8]["status"].replace("_", " ").title()
        third_party = response["components"][11]["status"].replace("_", " ").title()

        embed.add_field(
            name="Comment", value=f"{self.overall_status[comment]} {comment}"
        )

        with suppress(KeyError):
            embed.add_field(
                name="Last Updated", value=response["page"]["updated_at"]
            )

        embed.add_field(name="API", value=f"{self.component_status[api]} {api}")

        embed.add_field(
            name="Media Proxy",
            value=f"{self.component_status[media_proxy]} {media_proxy}",
        )
        embed.add_field(
            name="Push Notifications",
            value=f"{self.component_status[push_notifications]} {push_notifications}",
        )
        embed.add_field(
            name="Voice", value=f"{self.component_status[voice]} {voice}"
        )
        embed.add_field(
            name="Third Party",
            value=f"{self.component_status[third_party]} {third_party}",
        )

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                "https://srhpyqt94yxb.statuspage.io/api/v2/incidents.json"
            ) as response:
                response = await response.json()

        incident = response["incidents"][0]["name"]
        url = response["incidents"][0]["shortlink"]
        impact = response["incidents"][0]["impact"]
        state = response["incidents"][0]["status"]

        embed.add_field(
            name="Latest Incident",
            value=f"**[{impact.title()}]** [{incident}]({url}) ({state.title()})",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="gstatus")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _g_status(self, ctx: discord.Interaction):
        """Fetch GitHub overall and component status."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                "https://kctbh9vrtdwd.statuspage.io/api/v2/summary.json"
            ) as response:
                response = await response.json()

        embed = discord.Embed(colour=self.bot.embed_color)

        embed.title = "Github Status"

        comment = response["status"]["description"]
        git_operations = (
            response["components"][0]["status"].replace("_", " ").title()
        )
        git_api = response["components"][1]["status"].replace("_", " ").title()
        git_webhooks = response["components"][2]["status"].replace("_", " ").title()
        git_functions = response["components"][4]["status"].replace("_", " ").title()
        git_actions = response["components"][5]["status"].replace("_", " ").title()
        git_packages = response["components"][6]["status"].replace("_", " ").title()
        git_pages = response["components"][7]["status"].replace("_", " ").title()
        other = response["components"][8]["status"].replace("_", " ").title()

        embed.add_field(
            name="Comment",
            value=f"{self.overall_status[comment]} {comment}",
        )
        with suppress(KeyError):
            embed.add_field(
                name="Last Updated", value=response["page"]["updated_at"]
            )
        embed.add_field(
            name="GitHub Operations",
            value=f"{self.component_status[git_operations]} {git_operations}",
        )
        embed.add_field(
            name="API Requests", value=f"{self.component_status[git_api]} {git_api}"
        )
        embed.add_field(
            name="Webhooks",
            value=f"{self.component_status[git_webhooks]} {git_webhooks}",
        )
        embed.add_field(
            name="Issues, Pull Requests and Projects",
            value=f"{self.component_status[git_functions]} {git_functions}",
        )
        embed.add_field(
            name="GitHub Actions",
            value=f"{self.component_status[git_actions]} {git_actions}",
        )
        embed.add_field(
            name="Packages",
            value=f"{self.component_status[git_packages]} {git_packages}",
        )
        embed.add_field(
            name="GitHub Pages",
            value=f"{self.component_status[git_pages]} {git_pages}",
        )
        embed.add_field(
            name="Other", value=f"{self.component_status[other]} {other}"
        )

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                "https://kctbh9vrtdwd.statuspage.io/api/v2/incidents.json"
            ) as response:
                response = await response.json()

        incident = response["incidents"][0]["name"]
        url = response["incidents"][0]["shortlink"]
        impact = response["incidents"][0]["impact"]
        state = response["incidents"][0]["status"]

        embed.add_field(
            name="Latest Incident",
            value=f"**[{impact.upper()}]** [{incident}]({url}) ({state.title()})",
            inline=False,
        )

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="pypi")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _pypi(self, ctx: discord.Interaction, package: str):
        """Fetch information about a package from Python Package Index (PyPI).

        Parameters
        ----------
        package : str
            The package to look up.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(f"https://pypi.org/pypi/{package}/json") as res:
                if res.status == 200:
                    res = await res.json()
                    res = res["info"]

                    embed = discord.Embed(colour=self.bot.embed_color)
                    embed.title = f"PyPI Lookup - {res['name']}"
                    embed.description = res["summary"]
                    embed.url = res["package_url"]
                    embed.set_thumbnail(
                        url="https://pbs.twimg.com/profile_images/"
                        "909757546063323137/-RIWgodF_400x400.jpg"
                    )

                    with suppress(KeyError):
                        embed.add_field(
                            name="Version", value=f"{res['version']} (latest)"
                        )
                    with suppress(KeyError):
                        embed.add_field(
                            name="Author",
                            value=f"{res['author']} {'`(' + res['author_email'] + ')`' if res['author_email'] else ''}",
                        )

                    with suppress(KeyError):
                        embed.add_field(name="License", value=res["license"])

                    await ctx.edit_original_response(embed=embed)

                elif res.status == 404:
                    return await ctx.edit_original_response(
                        content=f"Couldn't find a package matching `{package}`."
                    )

                else:
                    return await ctx.edit_original_response(
                        content="An API-side error occurred while "
                        "processing your request. Please try again later."
                    )

    @app_commands.command(name="npm")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _npm(self, ctx: discord.Interaction, package: str):
        """Fetch information about a package from Node Package Manager (npm).

        Parameters
        ----------
        package : str
            The package to look up.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(f"https://registry.npmjs.org/{package}") as res:
                if res.status == 200:
                    res = await res.json()

                    embed = discord.Embed(colour=self.bot.embed_color)
                    embed.title = f"NPM Lookup - {res['name']}"
                    embed.description = res["description"]
                    embed.url = f"https://www.npmjs.com/package/{res['name']}"
                    embed.set_thumbnail(
                        url="https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png"
                    )

                    with suppress(KeyError):
                        embed.add_field(
                            name="Version",
                            value=f"{res['dist-tags']['latest']} (latest)",
                        )

                    with suppress(KeyError):
                        embed.add_field(
                            name="Author",
                            value=f"{res['author']['name']} "
                            f"{'`(' + res['author']['email'] + ')`' if res['author']['email'] else ''}",
                        )

                    with suppress(KeyError):
                        embed.add_field(name="License", value=res["license"])

                    await ctx.edit_original_response(embed=embed)

                elif res.status == 404:
                    return await ctx.edit_original_response(
                        content=f"Couldn't find a package matching `{package}`."
                    )

                else:
                    return await ctx.edit_original_response(
                        content="An API-side error occurred while "
                        "processing your request. Please try again later."
                    )

    @app_commands.command(name="screenshot")
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    @app_commands.choices(
        style=[
            app_commands.Choice(name="Normal", value="_"),
            app_commands.Choice(name="Full", value="_fullpage"),
            app_commands.Choice(name="Mobile", value="_galaxys5"),
            app_commands.Choice(name="Mobile Full", value="_galaxys5_fullpage"),
        ]
    )
    async def _screenshot(
        self,
        ctx: discord.Interaction,
        url: str,
        style: app_commands.Choice[str] = None,
    ):
        """Get the screenshot of a website.

        Parameters
        ----------
        url : str
            The URL to screenshot.

        style : app_commands.Choice[str], optional
            The style of the screenshot.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not validators.url(url):
            return await ctx.edit_original_response(
                content="The URL you have provided is invalid!"
            )

        style = style or app_commands.Choice(name="Normal", value="_")

        file_name = "".join(
            random.choices(
                string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10
            )
        )

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.get(
                    f"https://image.thum.io/get/width/1000/crop/1000/maxAge/0/"
                    f"noanimate{style.value.replace('_', '/')}/{url}"
                ) as res:
                    img = Image.open(BytesIO(await res.read()))

        except UnidentifiedImageError:
            return await ctx.edit_original_response(
                content=f"{url} is not a valid URL."
            )

        except asyncio.TimeoutError:
            return await ctx.edit_original_response(
                content="The screenshot operation timed out."
            )

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename=f"{file_name}.png")

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = f"Screenshot - {url}"
        embed.url = url
        embed.set_image(url=f"attachment://{file_name}.png")

        await ctx.edit_original_response(embed=embed, attachments=[file])

    @app_commands.command(
        name="tts",
        description="Convert a line of text to speech. "
        "Language has to be a valid IETF language tag (like en, fr etc).",
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_1)
    @app_commands.guild_only()
    async def _tts(self, ctx: discord.Interaction, language: str, text: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        try:
            tts = gtts.gTTS(text, lang=language)

        except ValueError:
            return await ctx.edit_original_response(
                content="The language specified is either not a valid "
                "IETF language tag (like `en`) or an unsupported one."
            )

        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)

        file_name = "".join(
            random.choices(
                string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10
            )
        )

        file = discord.File(buffer, filename=f"{file_name}.mp3")

        await ctx.edit_original_response(attachments=[file])


async def setup(bot: FumeTool):
    await bot.add_cog(Development(bot))
