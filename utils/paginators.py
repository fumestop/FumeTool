from __future__ import annotations
from typing import Optional

import discord
from discord.ext.menus import Menu, ListPageSource

import config

from utils.tools import format_boolean_text


class TagPaginatorSource(ListPageSource):
    def __init__(
        self,
        entries: list,
        ctx: discord.Interaction,
        member: Optional[discord.Member] = None,
        show_owner: Optional[bool] = True,
        per_page: Optional[int] = 10,
    ):
        super().__init__(entries, per_page=per_page)

        self.ctx: discord.Interaction = ctx
        self.member: discord.Member = member
        self.show_owner: bool = show_owner

    async def format_page(self, menu: Menu, page):
        embed = discord.Embed(color=config.EMBED_COLOR)
        embed.title = "Tags"
        embed.description = "\n".join(
            f"`{_tag['index']}.` **{_tag['name']}** "
            f"{'by ' + self.ctx.guild.get_member(_tag['user_id']).mention if self.show_owner else ''}"
            for _tag in page
        )

        if self.member:
            embed.set_author(
                name=self.member.nick or self.member.global_name,
                icon_url=(
                    self.member.avatar.url
                    if self.member.avatar
                    else self.member.default_avatar.url
                ),
            )

        embed.set_footer(
            text=f"{self.get_max_pages()} page(s) | {len(self.entries)} tag(s)"
        )

        return embed

    def is_paginating(self):
        return True


class RolePaginatorSource(ListPageSource):
    def __init__(
        self,
        entries: list,
        role: discord.Role,
        position: int,
        per_page: Optional[int] = 1,
    ):
        super().__init__(entries, per_page=per_page)

        self.role: discord.Role = role
        self.position: int = position

    async def format_page(self, menu: Menu, page):
        embed = discord.Embed(color=self.role.color)
        embed.title = f"Role Information for {self.role.name}"
        embed.add_field(name="ID", value=self.role.id)
        embed.add_field(name="Color", value=f"`{self.role.color}`")
        embed.add_field(
            name="Created",
            value=f"<t:{int(self.role.created_at.timestamp())}:F> (<t:{int(self.role.created_at.timestamp())}:R>)",
        )
        embed.add_field(name="Position", value=self.position)
        embed.add_field(name="User count", value=len(self.role.members))
        embed.add_field(
            name="Displayed separately",
            value=format_boolean_text(self.role.hoist),
        )
        embed.add_field(
            name="Mentionable", value=format_boolean_text(self.role.mentionable)
        )

        embed.add_field(name=page["name"], value=page["value"], inline=False)

        embed.set_footer(text=f"{self.get_max_pages()} permission categories")

        return embed

    def is_paginating(self):
        return True
