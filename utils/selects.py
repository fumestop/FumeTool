from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord import ui

from .modals import TagEditModal

from .db import get_tag, edit_tag, delete_tag

if TYPE_CHECKING:
    from bot import FumeTool


class TagEditSelect(ui.Select):
    def __init__(self, ctx: discord.Interaction, bot: FumeTool, options: list):
        super().__init__(
            placeholder="Select the tag to edit.",
            min_values=1,
            max_values=1,
            options=options,
        )

        self.ctx: discord.Interaction = ctx
        self.bot: FumeTool = bot

    async def callback(self, interaction: discord.Interaction):
        modal = TagEditModal()
        modal.title = "Edit Tag"
        modal.timeout = 300
        modal.ctx = self.ctx

        tag = await get_tag(
            self.bot.pool,
            guild_id=self.ctx.guild.id,
            name=self.values[0],
            check_alias=False,
        )
        modal.tag_content.default = tag["content"]

        # noinspection PyUnresolvedReferences
        await interaction.response.send_modal(modal)
        await modal.wait()

        await edit_tag(
            self.bot.pool,
            guild_id=self.ctx.guild.id,
            name=self.values[0],
            content=modal.tag_content.value,
        )

        await self.ctx.edit_original_response(
            content="The tag has been edited.", view=None
        )


class TagDeleteSelect(ui.Select):
    def __init__(self, ctx: discord.Interaction, bot: FumeTool, options: list):
        super().__init__(
            placeholder="Select the tag to delete.",
            min_values=1,
            max_values=1,
            options=options,
        )

        self.ctx: discord.Interaction = ctx
        self.bot: FumeTool = bot

    async def callback(self, interaction: discord.Interaction):
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        await delete_tag(
            self.bot.pool, guild_id=self.ctx.guild.id, name=self.values[0]
        )

        await self.ctx.edit_original_response(
            content="The tag has been deleted.", view=None
        )
