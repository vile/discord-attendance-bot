import shelve

import discord
from discord import app_commands
from discord.ext import commands, tasks


""" Shelve operations """  # fmt: skip
def shelve_get_instructors() -> list[int]:
    with shelve.open("database") as handle:
        return handle["instructors"] if "instructors" in handle else []


def shelve_add_instructor(user_id: discord.Member.id) -> bool:
    if user_id in shelve_get_instructors():
        return False

    with shelve.open("database") as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.append(user_id)
        handle["instructors"] = temp_instructors

    return user_id in shelve_get_instructors()


def shelve_remove_instructor(user_id: discord.Member.id) -> bool:
    if not user_id in shelve_get_instructors():
        return False

    with shelve.open("database") as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.remove(user_id)
        handle["instructors"] = temp_instructors

    return not user_id in shelve_get_instructors()


def shelve_take_member_snapshot(member_ids: list[int]) -> None:
    with shelve.open("database") as handle:
        temp_snapshots: list[dict] = handle["snapshots"]
        snapshot: list[int] = member_ids
        temp_snapshots.append(snapshot)
        handle["snapshots"] = temp_snapshots


def shelve_get_attendance_rate() -> float:
    with shelve.open("database") as handle:
        attendance_rate: float = handle["minimum_attendance_rate"]

    return attendance_rate


def shelve_set_attendace_rate(rate: float) -> bool:
    with shelve.open("database") as handle:
        handle["minimum_attendance_rate"] = rate

    return rate == shelve_get_attendance_rate()


def shelve_get_snapshot_interval() -> int:
    with shelve.open("database") as handle:
        snapshot_interval: int = handle["snapshot_interval"]

    return snapshot_interval


def shelve_set_snapshot_interval(interval: int) -> bool:
    with shelve.open("database") as handle:
        handle["snapshot_interval"] = interval

    return interval == shelve_get_snapshot_interval()


@app_commands.guild_only()
class AttendanceCommandsCog(
    commands.GroupCog,
    name="attendance",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.voice_channel = 0

        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.__cog_name__} cog loaded")
        await self.client.tree.sync()

    @app_commands.command()
    async def add_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_add_instructor(member.id)
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

    @app_commands.command()
    async def remove_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_remove_instructor(member.id)
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

    @app_commands.command()
    async def show_instructors(self, interaction: discord.Interaction) -> None:
        list_of_instructors: list[int] = shelve_get_instructors()
        formatted_message: str = ", ".join(f"<@{instructor}>" for instructor in list_of_instructors)  # fmt: skip
        if formatted_message == "":
            formatted_message = "There are no instructors to show!"

        await interaction.response.send_message(formatted_message, ephemeral=True)

    @app_commands.command()
    async def start_session(
        self, interaction: discord.Interaction, channel: discord.VoiceChannel
    ) -> None:
        if self.snapshot_task.is_running():
            await interaction.response.send_message(
                f"A session is already running in {self.client.get_channel(self.voice_channel).mention}. If you want to start a new session use `/{self.__cog_name__} start_session`",
                ephemeral=True,
            )
            return

        vc_members: list[int] = list(map(lambda member: member.id, channel.members))  # fmt: skip
        instructors: list[int] = shelve_get_instructors()
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

        self.voice_channel = channel.id
        self.snapshot_task.start()

        await interaction.response.send_message(
            f"Started a session in {channel.mention}!",
            ephemeral=True,
        )

    @app_commands.command()
    async def stop_session(self, interaction: discord.Interaction) -> None:
        if self.snapshot_task.is_being_cancelled():
            await interaction.response.send_message(
                "This session is already being canceled, please wait",
                ephemeral=True,
            )
            return

        if not self.snapshot_task.is_running():
            await interaction.response.send_message(
                "There is no currently running session, so there is nothing to stop",
                ephemeral=True,
            )
            return

        self.voice_channel = 0
        self.snapshot_task.cancel()

        await interaction.response.send_message(
            "Stopped session",
            ephemeral=True,
        )

    @app_commands.command()
    async def get_attendance(self, interaction: discord.Interaction) -> None:
        if self.snapshot_task.is_running():
            await interaction.response.send_message(
                "Can't report attendance while a session is active",
                ephemeral=True,
            )
            return

        with shelve.open("database") as handle:
            snapshots: list[int] = handle["snapshots"]

        if len(snapshots) == 0:
            await interaction.response.send_message(
                "No attendance to report",
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
        for member, attendance_count in attendance_total.items():
            if attendance_count / num_snapshots >= shelve_get_attendance_rate():
                attendance_met[member] = True
            else:
                attendance_met[member] = False

        message: str = f"Attendance for your recent session:\n- Total attended: {len(attendance_met.keys())}\n\nStatus:\n"
        for member, did_attend in attendance_met.items():
            pre_format: str = f"- <@{member}> "
            if did_attend:
                message += f"{pre_format} ✅ **ATTENDED**\n"
            else:
                message += f"{pre_format} ❌ **ABSENT**\n"

        await interaction.response.send_message(message)

    @app_commands.command()
    async def clear_attendance(self, interaction: discord.Interaction) -> None:
        with shelve.open("database") as handle:
            handle["snapshots"] = []

        await interaction.response.send_message(
            "Cleared attendance",
            ephemeral=True,
        )

    @app_commands.command()
    async def get_minium_attendance(self, interaction: discord.Interaction) -> None:
        attendance_rate: float = shelve_get_attendance_rate()

        await interaction.response.send_message(
            f"The current minimum attendance rate is {attendance_rate * 100:.0f}%",
            ephemeral=True,
        )

    @app_commands.command()
    async def set_minimum_attendance(
        self,
        interaction: discord.Interaction,
        rate: app_commands.Range[float, 0.0, 1.0],
    ) -> None:
        success: bool = shelve_set_attendace_rate(rate)

        if not success:
            await interaction.response.send_message(
                "There seems to have been an issue setting the attendance rate. Try again",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully set the required attendance rate to {rate * 100:.0f}%",
            ephemeral=True,
        )

    @app_commands.command()
    async def get_snapshot_interval(self, interaction: discord.Interaction) -> None:
        snapshot_interval: int = shelve_get_snapshot_interval()

        await interaction.response.send_message(
            f"The current snapshot rate is {snapshot_interval} seconds",
            ephemeral=True,
        )

    @app_commands.command()
    async def set_snapshot_interval(
        self, interaction: discord.Interaction, interval: app_commands.Range[int, 3, 15]
    ) -> None:
        if self.snapshot_task.is_running() or self.snapshot_task.is_being_cancelled():
            await interaction.response.send_message(
                "You can't set the snapshot interval while a session is running or being canceled. Stop your current session or wait a few seconds for the current session to finish canceling",
                ephemeral=True,
            )
            return

        success: bool = shelve_set_snapshot_interval(interval)

        if not success:
            await interaction.response.send_message(
                "There seems to have been an issue setting the snapshot interval. Try again",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully set the snapshot interval to {interval} seconds",
            ephemeral=True,
        )

    # TODO: Dynamically get task loop time (and set/get using shelve)
    @tasks.loop(seconds=3)
    # @tasks.loop(minutes=15)
    async def snapshot_task(self) -> None:
        if self.snapshot_task.is_being_cancelled():
            return

        try:
            target_vc_memberlist: list[discord.Member] = self.client.get_channel(self.voice_channel).members  # fmt: skip
        except AttributeError:
            return
        members_as_ids: list[int] = list(map(lambda member: member.id, target_vc_memberlist))  # fmt: skip
        instructors: list[int] = shelve_get_instructors()
        valid_instructor_in_channel: bool = False
        for instructor in instructors:
            if instructor in members_as_ids:
                valid_instructor_in_channel = True
                break

        if not valid_instructor_in_channel:
            self.snapshot_task.cancel()

        shelve_take_member_snapshot(members_as_ids)

    def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in shelve_get_instructors():
            return True
        elif self.client.is_owner(interaction.user):
            return True
        return False

    def cog_unload(self) -> None:
        self.voice_channel = 0
        self.snapshot_task.stop()

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: commands.CommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Sorry, you have to be an instructor to use this command.",
                ephemeral=True,
            )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(AttendanceCommandsCog(client))
