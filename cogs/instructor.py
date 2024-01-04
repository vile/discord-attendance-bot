import discord
from discord import app_commands
from discord.ext import commands

import cogs.utils.interaction_checks as interaction_checks
import cogs.utils.shelve_utils as shelve_utils


@app_commands.guild_only()
class InstructorCommandsCog(
    commands.GroupCog,
    name="instructor",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.__cog_name__} cog loaded")
        await self.client.tree.sync()

    @app_commands.command(name="add")
    async def add_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_utils.add_instructor(member.id)
        if not success:
            await interaction.response.send_message(
                "Sorry, I couldn't add this member as an instructor. Are they already an instructor?",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully added {member.mention} as an instructor!",
            ephemeral=True,
        )

    @app_commands.command(name="remove")
    async def remove_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_utils.remove_instructor(member.id)
        if not success:
            await interaction.response.send_message(
                "I couldn't remove this member. Are you sure they're an existing instructor?",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully removed  {member.mention} as an instructor!",
            ephemeral=True,
        )

    @app_commands.command(name="show")
    async def show_instructors(self, interaction: discord.Interaction) -> None:
        list_of_instructors: list[int] = shelve_utils.get_instructors()
        formatted_message: str = ", ".join(f"<@{instructor}>" for instructor in list_of_instructors)  # fmt: skip
        if formatted_message == "":
            formatted_message = "There are no instructors to show!"

        await interaction.response.send_message(formatted_message, ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await interaction_checks.user_is_instructor_or_owner(
            self.client, interaction
        ):
            return True
        return False

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: commands.CommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Sorry, you have to be an instructor to use this command.",
                ephemeral=True,
            )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(InstructorCommandsCog(client))