import discord
from discord import app_commands
from discord.ext import commands

import cogs.utils.interaction_checks as interaction_checks


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
            await interaction.response.send_message(
                "Sorry, you have to be an instructor to use this command.",
                ephemeral=True,
            )
