import logging
import os
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands, tasks

import cogs.utils.constants as constants
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

        permissions: discord.Permissions = interaction.channel.permissions_for(
            interaction.guild.get_member(self.client.application_id)
        )
        if not permissions.send_messages:
            await interaction.response.send_message(
                f"I can't send messages in this channel. Make sure I have permissions from one of my roles or through a channel override in {interaction.channel.mention}. Then, use this command again to get an attendance report.",
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

        embeds: list[discord.Embed] = []

        # Embed 1
        # - Attendance report header message
        # - Stats (total attended, total snapshots, present instructors?)

        header_embed: discord.Embed = discord.Embed(
            title="Attendance Report",
            description=f"- **Total Attended**: `{len(attendance_met.keys())}`\n- **Total Snapshots**: `{len(snapshots)}`\n- **Instructors Present**: {', '.join([f'<@{instructor}>' for instructor in instructors_present])}",
        )

        embeds.append(header_embed)

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

                self.logger.info("Max description length exceeded, appending new embed")
                embed: discord.Embed = discord.Embed(description=message)
                embeds.append(embed)
                message = ""
        else:
            if len(message) > 0 and len(embeds) < constants.MAXMIMUM_EMBEDS_PER_MESSAGE:
                embed: discord.Embed = discord.Embed(description=message)
                embeds.append(embed)

        content: str = ""
        if len(embeds) >= constants.MAXMIMUM_EMBEDS_PER_MESSAGE:
            content = ":bangbang: The amount of students present in this attendance report has exceeded the message length allowed by the Discord API. Therefore this message only shows a truncated list of students and their attendance."

        await interaction.response.send_message(
            content=content if content != "" else "", embeds=embeds
        )

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
    cog: AttendanceCommandsCog = AttendanceCommandsCog(client)
    await client.add_cog(cog, guild=discord.Object(int(os.getenv("GUILD_ID"))))
    cog.logger.info("Cog loaded")
