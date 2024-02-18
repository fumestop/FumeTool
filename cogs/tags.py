from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import discord
from discord import ui, app_commands
from discord.ext import commands
from discord.ext.menus.views import ViewMenuPages

from utils.cd import cooldown_level_0
from utils.modals import TagCreateModal
from utils.selects import TagEditSelect, TagDeleteSelect
from utils.paginators import TagPaginatorSource
from utils.db import (
    count_tags,
    create_tag,
    get_all_tags,
    get_tag,
    purge_tags,
    search_tags,
    get_tag_owner,
    update_tag_owner,
    get_tag_aliases,
    is_alias,
    update_tag_aliases,
)

if TYPE_CHECKING:
    from bot import FumeTool


@app_commands.guild_only()
class Tags(
    commands.GroupCog,
    group_name="tag",
    group_description="Various commands to create, view, edit, and delete tags in the server.",
):
    def __init__(self, bot: FumeTool):
        self.bot: FumeTool = bot

    @app_commands.command(name="view")
    @app_commands.rename(tag_name="name")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_view(self, ctx: discord.Interaction, tag_name: str):
        """Fetch a particular tag, by name.

        Parameters
        ----------
        tag_name : str
            The name of the tag to fetch.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(self.bot.pool, guild_id=ctx.guild.id, name=tag_name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        tag = await get_tag(self.bot.pool, guild_id=ctx.guild.id, name=tag_name)

        await ctx.edit_original_response(content=tag["content"])

    @app_commands.command(name="raw")
    @app_commands.rename(tag_name="name")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_raw(self, ctx: discord.Interaction, tag_name: str):
        """Fetch a particular tag, by name, and show its raw content.

        Parameters
        ----------
        tag_name : str
            The name of the tag to fetch.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(self.bot.pool, guild_id=ctx.guild.id, name=tag_name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        tag = await get_tag(self.bot.pool, guild_id=ctx.guild.id, name=tag_name)

        await ctx.edit_original_response(
            content=discord.utils.escape_markdown(tag["content"])
        )

    @app_commands.command(name="create")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_create(self, ctx: discord.Interaction):
        """Create a tag for the server, owned by you."""
        if not await count_tags(self.bot.pool, guild_id=ctx.guild.id) <= 100:
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                content="Sorry, this server already has the maximum number of tags allowed "
                "(**100**). Please delete one before adding another."
            )

        if (
            not await count_tags(
                self.bot.pool, guild_id=ctx.guild.id, user_id=ctx.user.id
            )
            <= 10
        ):
            # noinspection PyUnresolvedReferences
            return await ctx.response.send_message(
                content="Sorry, you have already created the maximum number of tags allowed "
                "(**10**) in this server. Please delete one before adding another."
            )

        modal = TagCreateModal()
        modal.ctx = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.send_modal(modal)
        await modal.wait()

        if await get_tag(
            self.bot.pool, guild_id=ctx.guild.id, name=modal.tag_name.value
        ):
            return await modal.interaction.edit_original_response(
                content="A tag/alias with this name already exists."
            )

        await create_tag(
            self.bot.pool,
            guild_id=ctx.guild.id,
            user_id=ctx.user.id,
            name=modal.tag_name.value,
            content=modal.tag_content.value,
        )

        await modal.interaction.edit_original_response(
            content="This tag has been added!"
        )

    @app_commands.command(name="alias")
    @app_commands.rename(tag_name="name")
    @app_commands.rename(alias_name="alias")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_alias(
        self, ctx: discord.Interaction, tag_name: str, alias_name: str
    ):
        """Add an alias for a pre-existing tag.

        Parameters
        ----------
        tag_name : str
            The name of the tag to add an alias for.
        alias_name : str
            The name of the alias to add.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(
            self.bot.pool, guild_id=ctx.guild.id, name=tag_name, check_alias=False
        ):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        if (
            len(
                await get_tag_aliases(
                    self.bot.pool, guild_id=ctx.guild.id, name=tag_name
                )
            )
            == 5
        ):
            return await ctx.edit_original_response(
                content="Sorry, a tag cannot have more than **5** aliases."
            )

        if await get_tag(
            self.bot.pool, guild_id=ctx.guild.id, name=alias_name
        ) or await is_alias(self.bot.pool, guild_id=ctx.guild.id, alias=alias_name):
            return await ctx.edit_original_response(
                content="This alias is already in use."
            )

        if "," in alias_name:
            return await ctx.edit_original_response(
                content="Alias names cannot have commas."
            )

        if len(alias_name) > 100:
            return await ctx.edit_original_response(
                content="Tag aliases cannot be more than **100 characters**."
            )

        await update_tag_aliases(
            self.bot.pool, guild_id=ctx.guild.id, name=tag_name, alias=alias_name
        )

        await ctx.edit_original_response(content="The alias has been added.")

    @app_commands.command(name="all")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_all(self, ctx: discord.Interaction):
        """List all the tags for the server."""
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await count_tags(self.bot.pool, guild_id=ctx.guild.id):
            return await ctx.edit_original_response(
                content="This server does not have any tags yet."
            )

        tags = await get_all_tags(self.bot.pool, guild_id=ctx.guild.id)

        pages = TagPaginatorSource(entries=tags, ctx=ctx)
        paginator = ViewMenuPages(
            source=pages,
            timeout=None,
            delete_message_after=False,
            clear_reactions_after=True,
        )

        await ctx.edit_original_response(content="\U0001F44C")
        await paginator.start(ctx)

    @app_commands.command(name="list")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_list(
        self, ctx: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """List all the tags a user created for the server.

        Parameters
        ----------
        member : Optional[discord.Member]
            The member whose tags are to be listed. Defaults to the author of the interaction.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        member = member or ctx.user

        if not await count_tags(
            self.bot.pool, guild_id=ctx.guild.id, user_id=member.id
        ):
            return await ctx.edit_original_response(
                content=f"{member.mention} has not created any tags in this server yet.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        tags = await get_all_tags(
            self.bot.pool, guild_id=ctx.guild.id, user_id=member.id
        )

        pages = TagPaginatorSource(
            entries=tags, ctx=ctx, member=member, show_owner=False
        )
        paginator = ViewMenuPages(
            source=pages,
            timeout=None,
            delete_message_after=False,
            clear_reactions_after=True,
        )

        await ctx.edit_original_response(content="\U0001F44C")
        await paginator.start(ctx)

    @app_commands.command(name="info")
    @app_commands.rename(tag_name="name")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_info(self, ctx: discord.Interaction, tag_name: str):
        """Get various information about a tag.

        Parameters
        ----------
        tag_name : str
            The name of the tag to get information about.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(self.bot.pool, guild_id=ctx.guild.id, name=tag_name):
            return await ctx.edit_original_response(
                content="No such tag found in this server."
            )

        tag = await get_tag(self.bot.pool, guild_id=ctx.guild.id, name=tag_name)

        embed = discord.Embed(colour=self.bot.embed_color)
        embed.title = "Tag Information"

        embed.add_field(name="Name", value=f"`{tag_name}`")

        owner = ctx.guild.get_member(tag["user_id"])
        embed.add_field(name="Owner", value=owner.mention if owner else "-")

        embed.add_field(
            name="Created",
            value=f"<t:{int(tag['created_at'].timestamp())}:F> (<t:{int(tag['created_at'].timestamp())}:R>)",
        )

        if tag["aliases"]:
            if await is_alias(self.bot.pool, guild_id=ctx.guild.id, alias=tag_name):
                embed.title = "Alias Information"

                embed.set_field_at(0, name="Original", value=f"`{tag['name']}`")

                aliases = tag["aliases"].split(",")
                aliases.pop(aliases.index(tag_name))
                aliases = list(map(lambda x: f"`{x}`", aliases))

                if len(aliases) != 0:
                    embed.add_field(name="Other aliases", value=", ".join(aliases))

            else:
                aliases = tag["aliases"].split(",")
                aliases = list(map(lambda x: f"`{x}`", aliases))

                if len(aliases) != 0:
                    embed.add_field(name="Aliases", value=", ".join(aliases))

        await ctx.edit_original_response(embed=embed)

    @app_commands.command(name="search")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    @app_commands.guild_only()
    async def _tag_search(self, ctx: discord.Interaction, query: str):
        """Search for tags by name.

        Parameters
        ----------
        query : str
            The query to search for.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        tags = await search_tags(self.bot.pool, guild_id=ctx.guild.id, query=query)

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

    @app_commands.command(name="edit")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_edit(
        self, ctx: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Edit a tag for the server.

        Parameters
        ----------
        member : Optional[discord.Member]
            The member whose tags are to be edited (requires `Manage Server` permission).

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if member and not ctx.user.guild_permissions.manage_guild:
            return await ctx.edit_original_response(
                content="You need the **Manage Server** permission in this server to edit other people's tags."
            )

        if not member and not await count_tags(
            self.bot.pool, guild_id=ctx.guild.id, user_id=ctx.user.id
        ):
            return await ctx.edit_original_response(
                content="You have not created any tags in this server yet."
            )

        if member and not await count_tags(
            self.bot.pool, guild_id=ctx.guild.id, user_id=member.id
        ):
            return await ctx.edit_original_response(
                content=f"{member.mention} has not created any tags in this server yet.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        options = list()

        for _tag in await get_all_tags(
            self.bot.pool,
            guild_id=ctx.guild.id,
            user_id=member.id if member else ctx.user.id,
        ):
            options.append(
                discord.SelectOption(
                    label=f"{_tag['index']}. {_tag['name']}", value=_tag["name"]
                )
            )

        item = TagEditSelect(ctx=ctx, bot=self.bot, options=options)
        view = ui.View(timeout=60)
        view.add_item(item=item)

        await ctx.edit_original_response(view=view)

    @app_commands.command(name="delete")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_delete(
        self, ctx: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Delete a tag from the server.

        Parameters
        ----------
        member : discord.Member, optional
            The member whose tags are to be deleted (requires `Manage Server` permission).

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if member and not ctx.user.guild_permissions.manage_guild:
            return await ctx.edit_original_response(
                content="You need the **Manage Server** permission in this server to delete other people's tags."
            )

        if not member and not await count_tags(
            self.bot.pool, guild_id=ctx.guild.id, user_id=ctx.user.id
        ):
            return await ctx.edit_original_response(
                content="You have not created any tags in this server yet."
            )

        if member and not await count_tags(
            self.bot.pool, guild_id=ctx.guild.id, user_id=member.id
        ):
            return await ctx.edit_original_response(
                content=f"{member.mention} has not created any tags in this server yet.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        options = list()

        for _tag in await get_all_tags(
            self.bot.pool,
            guild_id=ctx.guild.id,
            user_id=member.id if member else ctx.user.id,
        ):
            options.append(
                discord.SelectOption(
                    label=f"{_tag['index']}. {_tag['name']}", value=_tag["name"]
                )
            )

        item = TagDeleteSelect(ctx=ctx, bot=self.bot, options=options)
        view = ui.View(timeout=60)
        view.add_item(item=item)

        await ctx.edit_original_response(view=view)

    @app_commands.command(name="purge")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_purge(self, ctx: discord.Interaction, member: discord.Member):
        """Delete all the tags a specific member created in the server.

        Parameters
        ----------
        member : discord.Member
            The member whose tags are to be deleted.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not ctx.permissions.manage_guild:
            return await ctx.edit_original_response(
                content="You need the **Manage Server** permission in this server to purge tags."
            )

        if not await count_tags(
            self.bot.pool, guild_id=ctx.guild.id, user_id=member.id
        ):
            return await ctx.edit_original_response(
                content=f"{member.mention} has not created any tags in this server yet.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        await purge_tags(self.bot.pool, guild_id=ctx.guild.id, user_id=member.id)

        await ctx.edit_original_response(
            content=f"All the tags created by {member.mention} have been purged.",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @app_commands.command(name="claim")
    @app_commands.rename(tag_name="name")
    @app_commands.checks.dynamic_cooldown(cooldown_level_0)
    async def _tag_claim(self, ctx: discord.Interaction, tag_name: str):
        """Claim a tag whose original owner has left the server.

        Parameters
        ----------
        tag_name : str
            The name of the tag to claim.

        """
        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

        if not await get_tag(self.bot.pool, guild_id=ctx.guild.id, name=tag_name):
            return await ctx.edit_original_response(
                content="No such tag found for this server."
            )

        if (
            await get_tag_owner(self.bot.pool, guild_id=ctx.guild.id, name=tag_name)
            == ctx.user.id
        ):
            return await ctx.edit_original_response(
                content="You already own this tag."
            )

        if ctx.guild.get_member(
            await get_tag_owner(self.bot.pool, guild_id=ctx.guild.id, name=tag_name)
        ):
            return await ctx.edit_original_response(
                content="You can only claim a tag if its owner has left the server."
            )

        await update_tag_owner(
            self.bot.pool, guild_id=ctx.guild.id, user_id=ctx.user.id, name=tag_name
        )

        await ctx.edit_original_response(content="The tag has been claimed.")


async def setup(bot: FumeTool):
    await bot.add_cog(Tags(bot))
