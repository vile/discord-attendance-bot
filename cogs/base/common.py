import discord
from discord import Embed, app_commands
from discord.ext import commands

import cogs.utils.interaction_checks as interaction_checks
from cogs.utils.embed_generator import create_embed_error


class CommonBaseCog(commands.GroupCog):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await interaction_checks.user_is_instructor_or_owner(
            self.client, interaction
        ):
            return True

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: commands.CommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            embed: Embed = await create_embed_error(
                "Sorry, you have to be an instructor to use this command."
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
