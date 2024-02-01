import logging
import os
import typing

import discord
from discord import Embed, app_commands
from discord.ext import commands, tasks

import cogs.utils.descriptions as descriptions
import cogs.utils.shelve_utils as shelve_utils
from cogs.base.common import CommonBaseCog
from cogs.utils.embed_generator import create_embed, create_embed_error


@app_commands.guild_only()
class SettingCommandsCog(
    CommonBaseCog,
    name="settings",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger(f"cogs.{self.__cog_name__}")

    @app_commands.command(name="get-attendance", description=descriptions.SETTINGS_GET_MINIMUM_ATTENDANCE)  # fmt: skip
    async def get_minium_attendance(self, interaction: discord.Interaction) -> None:
        attendance_rate: float = shelve_utils.get_attendance_rate()

        embed: Embed = await create_embed(
            f"The current minimum attendance rate is **{attendance_rate * 100:.0f}%**"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="set-attendance", description=descriptions.SETTINGS_SET_MINIMUM_ATTENDANCE)  # fmt: skip
    @app_commands.describe(rate=descriptions.SETTINGS_SET_MINIMUM_ATTENDANCE_RATE)  # fmt: skip
    async def set_minimum_attendance(
        self,
        interaction: discord.Interaction,
        rate: app_commands.Range[float, 0.0, 1.0],
    ) -> None:
        success: bool = shelve_utils.set_attendace_rate(rate)

        if not success:
            embed: Embed = await create_embed_error(
                "There seems to have been an issue setting the attendance rate. Try again",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        embed: Embed = await create_embed(
            f"Successfully set the required attendance rate to **{rate * 100:.0f}%**",
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="get-interval", description=descriptions.SETTINGS_GET_INTERVAL)  # fmt: skip
    async def get_snapshot_interval(self, interaction: discord.Interaction) -> None:
        snapshot_interval: int = shelve_utils.get_snapshot_interval()

        embed: Embed = await create_embed(
            f"The current snapshot rate is **{snapshot_interval} seconds**"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="set-interval", description=descriptions.SETTINGS_SET_INTERVAL)  # fmt: skip
    @app_commands.describe(interval=descriptions.SETTINGS_SET_INTERVAL_INTERVAL)  # fmt: skip
    async def set_snapshot_interval(
        self,
        interaction: discord.Interaction,
        interval: app_commands.Range[int, 3, 900],
    ) -> None:
        attendance_cog: commands.GroupCog = self.client.get_cog("attendance")
        snapshot_task: tasks.Loop = attendance_cog.snapshot_task

        if snapshot_task.is_running() or snapshot_task.is_being_cancelled():
            embed: Embed = await create_embed_error(
                "You can't set the snapshot interval while a session is running or being canceled. Stop your current session or wait a few seconds for the current session to finish canceling",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        success: bool = shelve_utils.set_snapshot_interval(interval)

        if not success:
            embed: Embed = await create_embed_error(
                "There seems to have been an issue setting the snapshot interval. Try again",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        embed: Embed = await create_embed(
            f"Successfully set the snapshot interval to **{interval} seconds**",
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="get-auto-clear", description=descriptions.SETTINGS_GET_AUTO_CLEAR)  # fmt: skip
    async def get_auto_clear(
        self,
        interaction: discord.Interaction,
    ) -> None:
        should_clear_new_session: bool = shelve_utils.get_auto_clear_on_new_session()
        should_clear_after_attendance: bool = (
            shelve_utils.get_auto_clear_after_attendance_report()
        )

        embed: Embed = await create_embed(
            f"Auto clear `on new session`: **{should_clear_new_session}**\nAuto clear `after report`: **{should_clear_after_attendance}**"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="set-auto-clear", description=descriptions.SETTINGS_SET_AUTO_CLEAR)  # fmt: skip
    @app_commands.describe(on_event=descriptions.SETTINGS_SET_AUTO_CLEAR_ON_EVENT)  # fmt: skip
    @app_commands.describe(should_clear=descriptions.SETTINGS_SET_AUTO_CLEAR_SHOULD_CLEAR)  # fmt: skip
    async def set_auto_clear(
        self,
        interaction: discord.Interaction,
        on_event: typing.Literal["on new session", "after report"],
        should_clear: bool,
    ) -> None:
        if on_event == "on new session":
            success: bool = shelve_utils.set_auto_clear_on_new_session(should_clear)
        elif on_event == "after report":
            success: bool = shelve_utils.set_auto_clear_after_attendance_report(
                should_clear
            )

        if not success:
            embed: Embed = await create_embed_error(
                f"There seems to have been an issue setting auto clear for `{on_event}` to `{should_clear}`",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        embed: Embed = await create_embed(
            f"Successfully set auto clear for `{on_event}` to `{should_clear}`",
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )


async def setup(client: commands.Bot) -> None:
    cog: SettingCommandsCog = SettingCommandsCog(client)
    await client.add_cog(cog, guild=discord.Object(int(os.getenv("GUILD_ID"))))
    cog.logger.info("Cog loaded")
