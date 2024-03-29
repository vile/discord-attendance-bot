import logging
import os
import textwrap
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands, tasks

import cogs.utils.descriptions as descriptions
import cogs.utils.shelve_utils as shelve_utils
from cogs.base.common import CommonBaseCog
from cogs.enums.embed_type import EmbedType
from cogs.utils.macro import send_embed


@app_commands.guild_only()
class SettingCommandsCog(
    CommonBaseCog,
    name="settings",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger(f"cogs.{self.__cog_name__}")

    get_group: app_commands.Group = app_commands.Group(
        name="get", description="Get current settings"
    )

    @get_group.command(name="attendance", description=descriptions.SETTINGS_GET_MINIMUM_ATTENDANCE)  # fmt: skip
    async def get_minium_attendance(self, interaction: discord.Interaction) -> None:
        attendance_rate: float = shelve_utils.get_attendance_rate()

        await send_embed(
            interaction,
            message=f"The current minimum attendance rate is **{attendance_rate * 100:.0f}%**",
        )

    @get_group.command(name="interval", description=descriptions.SETTINGS_GET_INTERVAL)  # fmt: skip
    async def get_snapshot_interval(self, interaction: discord.Interaction) -> None:
        snapshot_interval: int = shelve_utils.get_snapshot_interval()

        await send_embed(
            interaction,
            message=f"The current snapshot rate is **{snapshot_interval} seconds**",
        )

    @get_group.command(name="auto-clear", description=descriptions.SETTINGS_GET_AUTO_CLEAR)  # fmt: skip
    async def get_auto_clear(self, interaction: discord.Interaction) -> None:
        should_clear_new_session: bool = shelve_utils.get_auto_clear_on_new_session()
        should_clear_after_attendance: bool = (
            shelve_utils.get_auto_clear_after_attendance_report()
        )

        message = textwrap.dedent(
            f"""
            - Auto clear `on new session`: **{should_clear_new_session}**
            - Auto clear `after report`: **{should_clear_after_attendance}**
            """
        )
        await send_embed(interaction, message=message)

    @get_group.command(name="ephemeral", description=descriptions.SETTINGS_GET_EPHEMERAL)  # fmt: skip
    async def get_attendance_commands_are_ephemeral(
        self, interaction: discord.Interaction
    ) -> None:
        responses_are_ephemeral: bool = (
            shelve_utils.get_important_attendance_responses_are_ephemeral()
        )

        await send_embed(
            interaction,
            message=f"Attendance command responses **{'are' if responses_are_ephemeral else 'are NOT'}** ephemeral",
        )

    set_group: app_commands.Group = app_commands.Group(
        name="set", description="Set new settings"
    )

    @set_group.command(name="attendance", description=descriptions.SETTINGS_SET_MINIMUM_ATTENDANCE)  # fmt: skip
    @app_commands.describe(rate=descriptions.SETTINGS_SET_MINIMUM_ATTENDANCE_RATE)  # fmt: skip
    async def set_minimum_attendance(
        self,
        interaction: discord.Interaction,
        rate: app_commands.Range[float, 0.0, 1.0],
    ) -> None:
        success: bool = shelve_utils.set_attendace_rate(rate)

        if not success:
            await send_embed(
                interaction,
                embed_type=EmbedType.ERROR,
                message="There seems to have been an issue setting the attendance rate. Try again",
            )
            return

        await send_embed(
            interaction,
            message=f"Successfully set the required attendance rate to **{rate * 100:.0f}%**",
        )

    @set_group.command(name="interval", description=descriptions.SETTINGS_SET_INTERVAL)  # fmt: skip
    @app_commands.describe(interval=descriptions.SETTINGS_SET_INTERVAL_INTERVAL)  # fmt: skip
    async def set_snapshot_interval(
        self,
        interaction: discord.Interaction,
        interval: app_commands.Range[int, 3, 900],
    ) -> None:
        attendance_cog: commands.GroupCog = self.client.get_cog("attendance")
        snapshot_task: tasks.Loop = attendance_cog.snapshot_task

        if snapshot_task.is_running():
            await send_embed(
                interaction,
                embed_type=EmbedType.ERROR,
                message="You can't set the snapshot interval while a session is running. Stop your current session to change the interval",
            )
            return

        success: bool = shelve_utils.set_snapshot_interval(interval)

        if not success:
            await send_embed(
                interaction,
                embed_type=EmbedType.ERROR,
                message="There seems to have been an issue setting the snapshot interval. Try again",
            )
            return

        await send_embed(
            interaction,
            message=f"Successfully set the snapshot interval to **{interval} seconds**",
        )

    @set_group.command(name="auto-clear", description=descriptions.SETTINGS_SET_AUTO_CLEAR)  # fmt: skip
    @app_commands.describe(on_event=descriptions.SETTINGS_SET_AUTO_CLEAR_ON_EVENT)  # fmt: skip
    @app_commands.describe(should_clear=descriptions.SETTINGS_SET_AUTO_CLEAR_SHOULD_CLEAR)  # fmt: skip
    async def set_auto_clear(
        self,
        interaction: discord.Interaction,
        on_event: Literal["on new session", "after report"],
        should_clear: bool,
    ) -> None:
        match on_event:
            case "on new session":
                success: bool = shelve_utils.set_auto_clear_on_new_session(should_clear)
            case "after report":
                success: bool = shelve_utils.set_auto_clear_after_attendance_report(
                    should_clear
                )
            case _:
                success: bool = False

        if not success:
            await send_embed(
                interaction,
                embed_type=EmbedType.ERROR,
                message=f"There seems to have been an issue setting auto clear for `{on_event}` to `{should_clear}`",
            )
            return

        await send_embed(
            interaction,
            message=f"Successfully set auto clear for `{on_event}` to `{should_clear}`",
        )

    @set_group.command(name="ephemeral", description=descriptions.SETTINGS_SET_EPHEMERAL)  # fmt: skip
    @app_commands.describe(are_ephemeral=descriptions.SETTINGS_SET_EPHEMERAL_ARE_EPHEMERAL)  # fmt: skip
    async def set_attendance_commands_are_ephemeral(
        self,
        interaction: discord.Interaction,
        are_ephemeral: bool,
    ) -> None:
        success: bool = shelve_utils.set_important_attendance_responses_are_ephemeral(
            are_ephemeral
        )

        if not success:
            await send_embed(
                interaction,
                embed_type=EmbedType.ERROR,
                message=f"There seems to have been a problem setting attendance commands to **{'ephemeral' if are_ephemeral else 'not ephemeral'}**. Try again",
            )
            return

        await send_embed(
            interaction,
            message=f"Successfully set attendance commands to **{'ephemeral' if are_ephemeral else 'not ephemeral'}**",
        )


async def setup(client: commands.Bot) -> None:
    cog: SettingCommandsCog = SettingCommandsCog(client)
    await client.add_cog(cog, guild=discord.Object(int(os.getenv("GUILD_ID"))))
    cog.logger.info("Cog loaded")
