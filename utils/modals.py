from __future__ import annotations
from typing import Optional

import discord
from discord import ui


class EvalModal(ui.Modal, title="Evaluate Code"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 300

    code = ui.TextInput(
        label="Code",
        placeholder="The code to evaluate...",
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )


class ExecModal(ui.Modal, title="Execute Shell Commands"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 300

    sh_commands = ui.TextInput(
        label="Command(s)",
        placeholder="The command(s) to execute...",
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )


class TagCreateModal(ui.Modal, title="Create Tag"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 300

    tag_name = ui.TextInput(
        label="Tag Name",
        placeholder="Enter the name of the tag (max. 25 characters)",
        min_length=1,
        max_length=25,
        required=True,
    )

    tag_content = ui.TextInput(
        label="Tag Content",
        placeholder="Enter the content of the tag (max. 2000 characters)",
        style=discord.TextStyle.paragraph,
        min_length=1,
        max_length=2000,
        required=True,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer(thinking=True)

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )


class TagEditModal(ui.Modal, title="Edit Tag"):
    ctx: Optional[discord.Interaction] = None
    interaction: Optional[discord.Interaction] = None

    timeout: int = 300

    tag_content = ui.TextInput(
        label="Tag Content",
        placeholder="Enter the content of the tag (max. 2000 characters)",
        style=discord.TextStyle.paragraph,
        min_length=1,
        max_length=2000,
        required=True,
    )

    async def on_submit(self, ctx: discord.Interaction):
        self.interaction = ctx

        # noinspection PyUnresolvedReferences
        await ctx.response.defer()

    async def on_timeout(self):
        await self.ctx.followup.send(
            content="Timeout! Please try again.", ephemeral=True
        )
