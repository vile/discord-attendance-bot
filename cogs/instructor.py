import logging
import os

import discord
from discord import Embed, app_commands
from discord.ext import commands

import cogs.utils.descriptions as descriptions
import cogs.utils.shelve_utils as shelve_utils
from cogs.base.common import CommonBaseCog
from cogs.utils.embed_generator import create_embed, create_embed_error


@app_commands.guild_only()
class InstructorCommandsCog(
    CommonBaseCog,
    name="instructor",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger(f"cogs.{self.__cog_name__}")

    @app_commands.command(name="add", description=descriptions.INSTRUCTOR_ADD)  # fmt: skip
    @app_commands.describe(member=descriptions.INSTRUCTOR_ADD_MEMBER)  # fmt: skip
    async def add_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_utils.add_instructor(member.id)
        if not success:
            embed: Embed = await create_embed_error(
                "Sorry, I couldn't add this member as an instructor. Are they already an instructor?",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        embed: Embed = await create_embed(
            f"Successfully added {member.mention} as an instructor"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="remove", description=descriptions.INSTRUCTOR_REMOVE)  # fmt: skip
    @app_commands.describe(member=descriptions.INSTRUCTOR_REMOVE_MEMBER)  # fmt: skip
    async def remove_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_utils.remove_instructor(member.id)
        if not success:
            embed: Embed = await create_embed_error(
                "I couldn't remove this member. Are you sure they're an existing instructor?",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        embed: Embed = await create_embed(
            f"Successfully removed  {member.mention} as an instructor"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="show", description=descriptions.INSTRUCTOR_SHOW)  # fmt: skip
    async def show_instructors(self, interaction: discord.Interaction) -> None:
        list_of_instructors: list[int] = shelve_utils.get_instructors()
        formatted_message: str = ", ".join(f"<@{instructor}>" for instructor in list_of_instructors)  # fmt: skip
        if formatted_message == "":
            formatted_message = "There are no instructors to show!"

        embed: Embed = await create_embed(formatted_message, title="Instructors")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot) -> None:
    cog: InstructorCommandsCog = InstructorCommandsCog(client)
    await client.add_cog(cog, guild=discord.Object(int(os.getenv("GUILD_ID"))))
    cog.logger.info("Cog loaded")
