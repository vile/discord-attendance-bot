import logging
import os
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands, tasks

import cogs.utils.descriptions as descriptions
import cogs.utils.shelve_utils as shelve_utils
from cogs.base.common import CommonBaseCog


@app_commands.guild_only()
class AttendanceCommandsCog(
    CommonBaseCog,
    name="attendance",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger(f"cogs.{self.__cog_name__}")
        self.voice_channel = 0

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.logger.info("cog loaded")

    @app_commands.command(name="start", description=descriptions.ATTENDANCE_START_SESSION)  # fmt: skip
    @app_commands.describe(channel=descriptions.ATTENDANCE_START_SESSION_CHANNEL)  # fmt: skip
    async def start_session(
        self,
        interaction: discord.Interaction,
        channel: Union[discord.VoiceChannel, discord.StageChannel],
    ) -> None:
        if self.snapshot_task.is_running():
            await interaction.response.send_message(
                f"A session is already running in {self.client.get_channel(self.voice_channel).mention}",
                ephemeral=True,
            )
            return

        vc_members: list[int] = list(map(lambda member: member.id, channel.members))  # fmt: skip
        instructors: list[int] = shelve_utils.get_instructors()
        valid_instructor_in_channel: bool = False
        for instructor in instructors:
            if instructor in vc_members:
                valid_instructor_in_channel = True
                break

        if not valid_instructor_in_channel:
            await interaction.response.send_message(
                f"You or another instructor needs to be in {channel.mention} to start a session",
                ephemeral=True,
            )
            return

        task_interval: int = shelve_utils.get_snapshot_interval()
        self.voice_channel = channel.id
        self.snapshot_task.change_interval(seconds=task_interval)
        self.snapshot_task.start()

        await interaction.response.send_message(
            f"Started a session in {channel.mention} and taking snapshots every {task_interval} seconds!",
            ephemeral=True,
        )

    @app_commands.command(name="stop", description=descriptions.ATTENDANCE_STOP_SESSION)  # fmt: skip
    async def stop_session(self, interaction: discord.Interaction) -> None:
        if self.snapshot_task.is_being_cancelled():
            await interaction.response.send_message(
                "This session is already being canceled, please wait",
                ephemeral=True,
            )
            return

        if not self.snapshot_task.is_running():
            await interaction.response.send_message(
                "A session is not currently running, so there is nothing to stop",
                ephemeral=True,
            )
            return

        self.voice_channel = 0
        self.snapshot_task.cancel()

        await interaction.response.send_message(
            "Successfully stopped the active session, no longer taking snapshots",
            ephemeral=True,
        )

    @app_commands.command(name="get", description=descriptions.ATTENDANCE_GET_ATTENDANCE)  # fmt: skip
    async def get_attendance(self, interaction: discord.Interaction) -> None:
        if self.snapshot_task.is_running():
            await interaction.response.send_message(
                "Can't report attendance while a session is active. Stop the current session if you want to get a report",
                ephemeral=True,
            )
            return

        snapshots: list[int] = shelve_utils.get_snapshots()

        if len(snapshots) == 0:
            await interaction.response.send_message(
                "No available stopshot data to report attendance with",
                ephemeral=True,
            )
            return

        attendance_total: dict = {}
        for snapshot in snapshots:
            for member in snapshot:
                if member in attendance_total:
                    attendance_total[member] += 1
                else:
                    attendance_total[member] = 1

        num_snapshots: int = len(snapshots)
        attendance_met: dict = {}
        attendance_rate: float = shelve_utils.get_attendance_rate()
        for member, attendance_count in attendance_total.items():
            if attendance_count / num_snapshots >= attendance_rate:
                attendance_met[member] = True
            else:
                attendance_met[member] = False

        message: str = f"Attendance for the recent attendance session:\n- Total Attended: {len(attendance_met.keys())}\n- Total Snapshots: {len(snapshots)}\n\nStatus:\n"
        for member, did_attend in attendance_met.items():
            pre_format: str = f"- <@{member}> "
            if did_attend:
                message += f"{pre_format} ✅ **ATTENDED**\n"
            else:
                message += f"{pre_format} ❌ **ABSENT**\n"

        await interaction.response.send_message(message)

    @app_commands.command(name="clear", description=descriptions.ATTENDANCE_CLEAR_ATTENDANCE)  # fmt: skip
    async def clear_attendance(self, interaction: discord.Interaction) -> None:
        success: bool = shelve_utils.clear_snapshots()
        if not success:
            await interaction.response.send_message(
                "Seems I couldn't clear attendance snapshots. Try again",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Successfully cleared attendance snapshots",
            ephemeral=True,
        )

    @tasks.loop()
    async def snapshot_task(self) -> None:
        if self.snapshot_task.is_being_cancelled():
            return

        try:
            target_vc_memberlist: list[discord.Member] = self.client.get_channel(self.voice_channel).members  # fmt: skip
        except AttributeError:
            return
        members_as_ids: list[int] = list(map(lambda member: member.id, target_vc_memberlist))  # fmt: skip
        instructors: list[int] = shelve_utils.get_instructors()
        valid_instructor_in_channel: bool = False
        for instructor in instructors:
            if instructor in members_as_ids:
                valid_instructor_in_channel = True
                break

        if not valid_instructor_in_channel:
            self.snapshot_task.cancel()

        self.logger.info(f"Taking member snapshot #{self.snapshot_task.current_loop}")
        shelve_utils.take_member_snapshot(members_as_ids)

    def cog_unload(self) -> None:
        self.voice_channel = 0
        self.snapshot_task.stop()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(
        AttendanceCommandsCog(client), guild=discord.Object(int(os.getenv("GUILD_ID")))
    )
