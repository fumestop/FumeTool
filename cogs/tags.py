import json

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.menus import Menu, ListPageSource
from discord.ext.menus.views import ViewMenuPages

from utils.cd import cooldown_level_0
from utils.db import (
    add_tag,
    all_tags,
    get_tag,
    edit_tag,
    delete_tag,
    search_tags,
    get_tag_owner,
    update_tag_owner,
    get_tag_aliases,
    is_alias,
    update_tag_aliases,
)


with open("config.json") as f:
    data = json.load(f)
    embed_color = int(hex(data["embed_color"]), 16)


class TagPaginatorSource(ListPageSource):
    def __init__(self, entries, ctx, per_page=20):
        self.ctx: discord.Interaction = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: Menu, page):
        embed = discord.Embed(color=embed_color)
        embed.title = "Tags"
        embed.description = ""

        for _index, _item in enumerate(page, 1):
            embed.description += f"**{_index}.** {_item}\n"

        return embed

    def is_paginating(self):
        return True


@app_commands.guild_only()
class Tags(
    commands.GroupCog,
    group_name="tag",
    group_description="Various commands to create, view, edit, and delete tags in the server.",
):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="view", description="Fetch a particular tag, by name.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_view(self, ctx: discord.Interaction, name: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(guild_id=ctx.guild.id, name=name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        tag = await get_tag(guild_id=ctx.guild.id, name=name)

        await ctx.edit_original_response(content=tag[4])

    @app_commands.command(
        name="raw", description="Show the raw content of a tag, fetched by name."
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_raw(self, ctx: discord.Interaction, name: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(guild_id=ctx.guild.id, name=name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        tag = await get_tag(guild_id=ctx.guild.id, name=name)

        await ctx.edit_original_response(content=discord.utils.escape_markdown(tag[4]))

    @app_commands.command(name="add", description="Add a tag for the server.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_add(self, ctx: discord.Interaction, name: str, content: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if await get_tag(guild_id=ctx.guild.id, name=name):
            return await ctx.edit_original_response(
                content="This tag already exists for this server."
            )

        if len(name) > 50:
            return await ctx.edit_original_response(
                content="Tag names cannot be more than **50 characters**."
            )

        tags = await all_tags(guild_id=ctx.guild.id)

        if len(tags) == 10:
            return await ctx.edit_original_response(
                content="Sorry, this server already has the maximum number of tags allowed "
                "(**10**). Please delete one before adding another."
            )

        await add_tag(
            guild_id=ctx.guild.id, user_id=ctx.user.id, name=name, content=content
        )

        await ctx.edit_original_response(content="This tag has been added!")

    @app_commands.command(name="list", description="List all the tags for the server.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_list(self, ctx: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        tags = await all_tags(guild_id=ctx.guild.id)

        if not tags:
            return await ctx.edit_original_response(
                content="This server does not have any tags set yet."
            )

        else:
            pages = TagPaginatorSource(entries=tags, ctx=ctx)
            paginator = ViewMenuPages(
                source=pages,
                timeout=None,
                delete_message_after=False,
                clear_reactions_after=True,
            )

            await ctx.edit_original_response(content="\U0001F44C")
            await paginator.start(ctx)

    @app_commands.command(name="edit", description="Edit a tag for the server.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_edit(self, ctx: discord.Interaction, name: str, content: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(guild_id=ctx.guild.id, name=name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        if (
            await get_tag_owner(guild_id=ctx.guild.id, name=name) != ctx.user.id
            and not ctx.user.guild_permissions.manage_guild
        ):
            return await ctx.edit_original_response(
                content="You do not have permission to edit this tag. "
                "Either you have to be the tag owner or you should have "
                "the **Manage Server** permission in this server."
            )

        await edit_tag(guild_id=ctx.guild.id, name=name, content=content)

        await ctx.edit_original_response(content="The tag has been edited.")

    @app_commands.command(name="delete", description="Delete a tag for the server.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _tag_delete(self, ctx: discord.Interaction, name: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(guild_id=ctx.guild.id, name=name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        if (
            await get_tag_owner(guild_id=ctx.guild.id, name=name) != ctx.user.id
            and not ctx.user.guild_permissions.manage_guild
        ):
            return await ctx.edit_original_response(
                content="You do not have permission to delete this tag. "
                "Either you have to be the tag owner or you should have "
                "the **Manage Server** permission in this server."
            )

        await delete_tag(guild_id=ctx.guild.id, name=name)

        await ctx.edit_original_response(content="The tag has been deleted.")

    @app_commands.command(
        name="claim",
        description="Claim a tag whose original owner has left the server.",
    )
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _tag_claim(self, ctx: discord.Interaction, name: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(guild_id=ctx.guild.id, name=name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        if await get_tag_owner(guild_id=ctx.guild.id, name=name) == ctx.user.id:
            return await ctx.edit_original_response(content="You already own this tag.")

        if ctx.guild.get_member(await get_tag_owner(guild_id=ctx.guild.id, name=name)):
            return await ctx.edit_original_response(
                content="You can only claim a tag if its owner has left the server."
            )

        await update_tag_owner(guild_id=ctx.guild.id, user_id=ctx.user.id, name=name)

        await ctx.edit_original_response(content="The tag has been claimed.")

    @app_commands.command(name="alias", description="Add an alias for a tag.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _tag_alias(self, ctx: discord.Interaction, name: str, alias: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(guild_id=ctx.guild.id, name=name, check_alias=False):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        if len(await get_tag_aliases(guild_id=ctx.guild.id, name=name)) == 5:
            return await ctx.edit_original_response(
                content="Sorry, a tag cannot have more than **5** aliases."
            )

        if await get_tag(
            guild_id=ctx.guild.id, name=alias
        ) is not None or await is_alias(guild_id=ctx.guild.id, alias=alias):
            return await ctx.edit_original_response(
                content="This alias is already in use."
            )

        if "|" in alias:
            return await ctx.edit_original_response(
                content="Alias names cannot have the pipe (`|`) character in them."
            )

        if len(alias) > 100:
            return await ctx.edit_original_response(
                content="Tag aliases cannot be more than **100 characters**."
            )

        await update_tag_aliases(guild_id=ctx.guild.id, name=name, alias=alias)

        await ctx.edit_original_response(content="The alias has been added.")

    @app_commands.command(name="info", description="Get information about a tag.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _tag_info(self, ctx: discord.Interaction, name: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(guild_id=ctx.guild.id, name=name):
            return await ctx.edit_original_response(
                content="No such tag found in this server."
            )

        tag = await get_tag(guild_id=ctx.guild.id, name=name)

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Tag"

        embed.add_field(name="Name", value=f"`{name}`")

        owner = ctx.guild.get_member(tag[1])
        embed.add_field(name="Owner", value=owner.mention if owner else "Unclaimed")

        embed.add_field(
            name="Created",
            value=f"<t:{int(tag[3].timestamp())}:F> (<t:{int(tag[3].timestamp())}:R>)",
        )

        if tag[5]:
            if await is_alias(guild_id=ctx.guild.id, alias=name):
                embed.title = "Alias"

                embed.set_field_at(0, name="Original", value=f"`{tag[2]}`")

                aliases = tag[5].split("|")
                aliases.pop(aliases.index(name))

                if len(aliases) != 0:
                    embed.add_field(name="Other aliases", value=", ".join(aliases))

            else:
                aliases = tag[5].split("|")

                if len(aliases) != 0:
                    embed.add_field(name="Aliases", value=", ".join(aliases))

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="search", description="Search for tags by name.")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _tag_search(self, ctx: discord.Interaction, query: str):
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        tags = await search_tags(guild_id=ctx.guild.id, query=query)

        if not tags:
            await ctx.edit_original_response(content="No such tags found.")

        else:
            pages = TagPaginatorSource(entries=tags, ctx=ctx)
            paginator = ViewMenuPages(
                source=pages,
                timeout=None,
                delete_message_after=False,
                clear_reactions_after=True,
            )

            await ctx.edit_original_response(content="\U0001F44C")
            await paginator.start(ctx)


async def setup(bot):
    await bot.add_cog(Tags(bot))
