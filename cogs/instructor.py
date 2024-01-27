import os

import discord
from discord import app_commands
from discord.ext import commands

import cogs.utils.descriptions as descriptions
import cogs.utils.shelve_utils as shelve_utils
from cogs.base.common import CommonBaseCog


@app_commands.guild_only()
class InstructorCommandsCog(
    CommonBaseCog,
    name="instructor",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.__cog_name__} cog loaded")

    @app_commands.command(name="add", description=descriptions.INSTRUCTOR_ADD)  # fmt: skip
    @app_commands.describe(member=descriptions.INSTRUCTOR_ADD_MEMBER)  # fmt: skip
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
            f"Successfully added {member.mention} as an instructor",
            ephemeral=True,
        )

    @app_commands.command(name="remove", description=descriptions.INSTRUCTOR_REMOVE)  # fmt: skip
    @app_commands.describe(member=descriptions.INSTRUCTOR_REMOVE_MEMBER)  # fmt: skip
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
            f"Successfully removed  {member.mention} as an instructor",
            ephemeral=True,
        )

    @app_commands.command(name="show", description=descriptions.INSTRUCTOR_SHOW)  # fmt: skip
    async def show_instructors(self, interaction: discord.Interaction) -> None:
        list_of_instructors: list[int] = shelve_utils.get_instructors()
        formatted_message: str = ", ".join(f"<@{instructor}>" for instructor in list_of_instructors)  # fmt: skip
        if formatted_message == "":
            formatted_message = "There are no instructors to show!"

        await interaction.response.send_message(formatted_message, ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(
        InstructorCommandsCog(client), guild=discord.Object(int(os.getenv("GUILD_ID")))
    )
