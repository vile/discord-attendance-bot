import logging
import os
import textwrap
import time
from datetime import datetime
from typing import Union

import discord
from discord import Embed, app_commands
from discord.ext import commands, tasks

import cogs.utils.constants as constants
import cogs.utils.descriptions as descriptions
import cogs.utils.shelve_utils as shelve_utils
from cogs.base.common import CommonBaseCog
from cogs.utils.embed_generator import create_embed, create_embed_error
from cogs.views.attendance_export import AttendanceExportButtons


@app_commands.guild_only()
class AttendanceCommandsCog(
    CommonBaseCog,
    name="attendance",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger(f"cogs.{self.__cog_name__}")
        self.voice_channel = 0

    @app_commands.command(name="start", description=descriptions.ATTENDANCE_START_SESSION)  # fmt: skip
    @app_commands.describe(channel=descriptions.ATTENDANCE_START_SESSION_CHANNEL)  # fmt: skip
    async def start_session(
        self,
        interaction: discord.Interaction,
        channel: Union[discord.VoiceChannel, discord.StageChannel],
    ) -> None:
        if self.snapshot_task.is_running():
            embed: Embed = await create_embed_error(
                f"A session is already running in {self.client.get_channel(self.voice_channel).mention}",
            )
            await interaction.response.send_message(
                embed=embed,
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
            embed: Embed = await create_embed_error(
                f"You or another instructor needs to be in {channel.mention} to start a session",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        should_clear: bool = shelve_utils.get_auto_clear_on_new_session()
        if should_clear:
            cleared_success: bool = shelve_utils.clear_snapshots()

        task_interval: int = shelve_utils.get_snapshot_interval()
        self.voice_channel = channel.id
        self.snapshot_task.change_interval(seconds=task_interval)
        self.snapshot_task.start()

        auto_clear_message: str = ""
        if should_clear and cleared_success:
            auto_clear_message = "Snapshots have been auto cleared for this new session"
        elif should_clear and not cleared_success:
            auto_clear_message = "Snapshots failed to auto clear, if you wish to clear snapshot data, stop this session and manually clear snapshots"
        elif not should_clear:
            auto_clear_message = "Snapshot auto clear is disabled"

        message_is_ephemeral: bool = (
            shelve_utils.get_important_attendance_responses_are_ephemeral()
        )
        embed: Embed = await create_embed(
            f"Started a session in {channel.mention} and taking snapshots every {task_interval} seconds! **{auto_clear_message}**"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=message_is_ephemeral,
        )

    @app_commands.command(name="stop", description=descriptions.ATTENDANCE_STOP_SESSION)  # fmt: skip
    async def stop_session(self, interaction: discord.Interaction) -> None:
        if self.snapshot_task.is_being_cancelled():
            embed: Embed = await create_embed_error(
                "This session is already being canceled, please wait",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        if not self.snapshot_task.is_running():
            embed: Embed = await create_embed_error(
                "A session is not currently running, so there is nothing to stop",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        self.voice_channel = 0
        self.snapshot_task.cancel()

        message_is_ephemeral: bool = (
            shelve_utils.get_important_attendance_responses_are_ephemeral()
        )
        embed: Embed = await create_embed(
            "Successfully stopped the active session, no longer taking snapshots",
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=message_is_ephemeral,
        )

    @app_commands.command(name="stats", description=descriptions.ATTENDANCE_STATS_SESSION)  # fmt: skip
    async def get_stats_for_current_session(
        self, interaction: discord.Interaction
    ) -> None:
        if not self.snapshot_task.is_running():
            embed: Embed = await create_embed_error(
                f"No active session is running to get stats for"
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        snapshot_interval: int = shelve_utils.get_snapshot_interval()
        snapshots: list[int] = shelve_utils.get_snapshots()
        num_snapshots: int = len(snapshots)
        # Since the exact starting timestamp is not recorded, we can guess the
        # rough start time (within one `snapshot_interval`), which is close enough
        assumed_session_length: int = num_snapshots * snapshot_interval
        assumed_started_timestamp: datetime = datetime.fromtimestamp(
            int(time.time()) - assumed_session_length
        )

        message_for_embed: str = textwrap.dedent(
            f"""
            - **Number of Snapshots**: `{num_snapshots}`
            - **Snapshot Interval**: `{snapshot_interval}` seconds
            - **Start Time**: ~{discord.utils.format_dt(assumed_started_timestamp)} ({discord.utils.format_dt(assumed_started_timestamp, style='R')})
            """
        )

        message_is_ephemeral: bool = (
            shelve_utils.get_important_attendance_responses_are_ephemeral()
        )
        embed: Embed = await create_embed(
            message_for_embed,
            title="Active session stats",
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=message_is_ephemeral,
        )

    @app_commands.command(name="get", description=descriptions.ATTENDANCE_GET_ATTENDANCE)  # fmt: skip
    async def get_attendance(self, interaction: discord.Interaction) -> None:
        if self.snapshot_task.is_running():
            embed: Embed = await create_embed_error(
                "Can't report attendance while a session is active. Stop the current session if you want to get a report",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        permissions: discord.Permissions = interaction.channel.permissions_for(
            interaction.guild.get_member(self.client.application_id)
        )
        if not permissions.send_messages:
            embed: Embed = await create_embed_error(
                f"I can't send messages in this channel. Make sure I have permissions from one of my roles or through a channel override in {interaction.channel.mention}. Then, use this command again to get an attendance report",
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        snapshots: list[int] = shelve_utils.get_snapshots()

        if len(snapshots) == 0:
            embed: Embed = await create_embed_error(
                "No available stopshot data to report attendance with",
            )
            await interaction.response.send_message(
                embed=embed,
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
        instructors: list[int] = shelve_utils.get_instructors()
        instructors_present: list[int] = []
        for member, attendance_count in attendance_total.items():
            if member in instructors:
                instructors_present.append(member)
                continue

            if attendance_count / num_snapshots >= attendance_rate:
                attendance_met[member] = True
            else:
                attendance_met[member] = False

        should_clear: bool = shelve_utils.get_auto_clear_after_attendance_report()
        if should_clear:
            cleared_success: bool = shelve_utils.clear_snapshots()

        embeds: list[discord.Embed] = []

        # Embed 1
        # - Attendance report header message
        # - Stats (total attended, total snapshots, present instructors, auto clear snapshots on/off + success/fail)

        snapshot_interval: int = shelve_utils.get_snapshot_interval()
        assumed_session_length: int = num_snapshots * snapshot_interval
        assumed_started_timestamp: datetime = datetime.fromtimestamp(
            int(time.time()) - assumed_session_length
        )

        header_embed: discord.Embed = discord.Embed(
            title="Attendance Report",
            description=textwrap.dedent(
                f"""
                - **Class Size**: `{len(attendance_met.keys())}`
                - **Total Snapshots**: `{len(snapshots)}`
                - **Instructors Present**: {', '.join([f'<@{instructor}>' for instructor in instructors_present])}
                - **Auto Clear Snapshots**: {'`on`' if should_clear else '`off`'} {'(success)' if should_clear and cleared_success else ''}
                - **Start Time**: ~{discord.utils.format_dt(assumed_started_timestamp)} ({discord.utils.format_dt(assumed_started_timestamp, style='R')})
                """
            ),
        )

        embeds.append(header_embed)

        # Check if there are zero non-instructor users
        if len(attendance_met.keys()) == 0:
            embed: discord.Embed = discord.Embed(
                description="No students attended this session"
            )
            embeds.append(embed)
        else:
            # Embed 2, 3, ...
            # - List of attended/absent members

            message: str = ""
            for member, did_attend in attendance_met.items():
                pre_format: str = f"- <@{member}>"
                if did_attend:
                    message += f"{pre_format} ✅ **ATTENDED**\n"
                else:
                    message += f"{pre_format} ❌ **ABSENT**\n"

                if len(message) >= constants.MAXMIMUM_EMBED_DESCRIPTION_LENGTH:
                    if len(embeds) >= constants.MAXMIMUM_EMBEDS_PER_MESSAGE:
                        # Do not add any embeds past 10, Discord API only allows up to 10 embeds per response
                        break

                    self.logger.info(
                        "Max description length exceeded, appending new embed"
                    )
                    embed: discord.Embed = discord.Embed(description=message)
                    embeds.append(embed)
                    message = ""
            else:
                if (
                    len(message) > 0
                    and len(embeds) < constants.MAXMIMUM_EMBEDS_PER_MESSAGE
                ):
                    embed: discord.Embed = discord.Embed(description=message)
                    embeds.append(embed)

        content: str = ""
        if len(embeds) >= constants.MAXMIMUM_EMBEDS_PER_MESSAGE:
            content = ":bangbang: The amount of students present in this attendance report has exceeded the message length allowed by the Discord API. Therefore this message only shows a truncated list of students and their attendance."

        view = AttendanceExportButtons(attendance_data=attendance_met)
        await interaction.response.send_message(
            content=content if content != "" else "",
            embeds=embeds,
            view=view,
        )

    @app_commands.command(name="clear", description=descriptions.ATTENDANCE_CLEAR_ATTENDANCE)  # fmt: skip
    async def clear_attendance(self, interaction: discord.Interaction) -> None:
        success: bool = shelve_utils.clear_snapshots()
        if not success:
            embed: Embed = await create_embed_error(
                "Seems I couldn't clear attendance snapshots. Try again"
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
            return

        message_is_ephemeral: bool = (
            shelve_utils.get_important_attendance_responses_are_ephemeral()
        )
        embed: Embed = await create_embed("Successfully cleared attendance snapshots")
        await interaction.response.send_message(
            embed=embed,
            ephemeral=message_is_ephemeral,
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
    cog: AttendanceCommandsCog = AttendanceCommandsCog(client)
    await client.add_cog(cog, guild=discord.Object(int(os.getenv("GUILD_ID"))))
    cog.logger.info("Cog loaded")
