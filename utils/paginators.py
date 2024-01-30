from __future__ import annotations
from typing import Optional

import discord
from discord.ext.menus import Menu, ListPageSource

import config


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
        embed = discord.Embed(color=config.embed_color)
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
            text=f"{self.get_max_pages()} pages | {len(self.entries)} tags"
        )

        return embed

    def is_paginating(self):
        return True
